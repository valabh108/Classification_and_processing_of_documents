# from Predictor import predict
import getpass
import pandas as pd
import os
os.environ["GROQ_API_KEY"] = "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"
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama3-8b-8192")

def predict_llms(text):
    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage("the given text is extracted from a scanned PDF document using OCR. Based on the text, return what type of document label it is in maximum of 3 words only .Refrain from using any adjectives, be as straight forward and to the point as possible. For example: cards, credit cards, application form, etc. If nothing can be deduced directly, return Nan."),
        HumanMessage(text),
    ]

    return llm.invoke(messages).content




