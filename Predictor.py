import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from transformers import LayoutLMForSequenceClassification, LayoutLMTokenizer
import torch
from torch.utils.data import Dataset, DataLoader
import pytesseract
from datasets import Features, Sequence, ClassLabel, Value, Array2D
import numpy as np
from datasets import Dataset
from pdf2image import convert_from_path
from Edgecase_Classification_using_llm import predict_llms
classes = ['invoice', 'resume', 'passport', 'Tax_Statement', 'balance_sheet', 'Income_Statement', 'Driving_License', ]


def normalize_box(box, width, height):
     return [
         int(1000 * (box[0] / width)),
         int(1000 * (box[1] / height)),
         int(1000 * (box[2] / width)),
         int(1000 * (box[3] / height)),
     ]

def apply_ocr(example):
        # get the image
        image = convert_from_path(example['file_path'])[0]

        width, height = image.size

        # apply ocr to the image
        ocr_df = pytesseract.image_to_data(image, output_type='data.frame')
        float_cols = ocr_df.select_dtypes('float').columns
        ocr_df = ocr_df.dropna().reset_index(drop=True)
        ocr_df[float_cols] = ocr_df[float_cols].round(0).astype(int)
        ocr_df = ocr_df.replace(r'^\s*$', np.nan, regex=True)
        ocr_df = ocr_df.dropna().reset_index(drop=True)

        # get the words and actual (unnormalized) bounding boxes
        #words = [word for word in ocr_df.text if str(word) != 'nan'])
        words = list(ocr_df.text)
        words = [str(w) for w in words]
        coordinates = ocr_df[['left', 'top', 'width', 'height']]
        actual_boxes = []
        for idx, row in coordinates.iterrows():
            x, y, w, h = tuple(row) # the row comes in (left, top, width, height) format
            actual_box = [x, y, x+w, y+h] # we turn it into (left, top, left+width, top+height) to get the actual box
            actual_boxes.append(actual_box)

        # normalize the bounding boxes
        boxes = []
        for box in actual_boxes:
            boxes.append(normalize_box(box, width, height))

        # add as extra columns
        assert len(words) == len(boxes)
        example['words'] = words
        example['bbox'] = boxes
        return example
tokenizer = LayoutLMTokenizer.from_pretrained("microsoft/layoutlm-base-uncased")
label2idx = {'invoice': 0, 'resume': 1, 'passport':2, 'Tax_Statement':3, 'balance_sheet':4, 'Income_Statement':5, 'Driving_License':6}

def encode_example(example, max_seq_length=512, pad_token_box=[0, 0, 0, 0]):
  words = example['words']
  normalized_word_boxes = example['bbox']

  assert len(words) == len(normalized_word_boxes)

  token_boxes = []
  for word, box in zip(words, normalized_word_boxes):
      word_tokens = tokenizer.tokenize(word)
      token_boxes.extend([box] * len(word_tokens))

  # Truncation of token_boxes
  special_tokens_count = 2
  if len(token_boxes) > max_seq_length - special_tokens_count:
      token_boxes = token_boxes[: (max_seq_length - special_tokens_count)]

  # add bounding boxes of cls + sep tokens
  token_boxes = [[0, 0, 0, 0]] + token_boxes + [[1000, 1000, 1000, 1000]]

  encoding = tokenizer(' '.join(words), padding='max_length', truncation=True)
  # Padding of token_boxes up the bounding boxes to the sequence length.
  input_ids = tokenizer(' '.join(words), truncation=True)["input_ids"]
  padding_length = max_seq_length - len(input_ids)
  token_boxes += [pad_token_box] * padding_length
  encoding['bbox'] = token_boxes

  assert len(encoding['input_ids']) == max_seq_length
  assert len(encoding['attention_mask']) == max_seq_length
  assert len(encoding['token_type_ids']) == max_seq_length
  assert len(encoding['bbox']) == max_seq_length

  return encoding

# we need to define the features ourselves as the bbox of LayoutLM are an extra feature
features = Features({
    'input_ids': Sequence(feature=Value(dtype='int64')),
    'bbox': Array2D(dtype="int64", shape=(512, 4)),
    'attention_mask': Sequence(Value(dtype='int64')),
    'token_type_ids': Sequence(Value(dtype='int64')),
    'label': ClassLabel(names=['refuted', 'entailed']),
    'image_path': Value(dtype='string'),
    'words': Sequence(feature=Value(dtype='string')),
})
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LayoutLMForSequenceClassification.from_pretrained("./saved_model")
model.to(device)
import pytesseract
import numpy as np
import torch.nn.functional as F

def predict(test_data):

    human_needed = False
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
    test_dataset = Dataset.from_pandas(test_data)
    updated_test_dataset = test_dataset.map(apply_ocr)

    df = pd.DataFrame.from_dict(updated_test_dataset)
    text = " ".join(df['words'][0])

    encoded_test_dataset = updated_test_dataset.map(lambda example: encode_example(example))

    encoded_test_dataset.set_format(type='torch', columns=['input_ids', 'bbox', 'attention_mask', 'token_type_ids'])

    test_dataloader = torch.utils.data.DataLoader(encoded_test_dataset, batch_size=1, shuffle=False)

    for test_batch in test_dataloader:

        input_ids = test_batch["input_ids"].to(device)
        bbox = test_batch["bbox"].to(device)
        attention_mask = test_batch["attention_mask"].to(device)
        token_type_ids = test_batch["token_type_ids"].to(device)

        # forward pass
        outputs = model(input_ids=input_ids, bbox=bbox, attention_mask=attention_mask,
                        token_type_ids=token_type_ids)

        classification_logits = outputs.logits
        classification_results = torch.softmax(classification_logits, dim=1).tolist()[0]
        # for i in range(len(classes)):
        #     print(f"{classes[i]}: {int(round(classification_results[i] * 100))}%")
        res = []
        for i in range(len(classes)):
            res.append(int(round(classification_results[i] * 100)))
        if any(value > 90 for value in res):
            prediction = (outputs.logits.argmax(-1).squeeze().tolist())
            return text, classes[prediction], human_needed

        else:
            prediction = predict_llms(text)
            human_needed = True
            return text, prediction, human_needed

        # print(test_batch['label'])



# file_path = './IMG_6008.pdf'
# data = {'file_path': [file_path]}
# df = pd.DataFrame(data)
# text, l = predict(df)
# print(l)
# print(text)
