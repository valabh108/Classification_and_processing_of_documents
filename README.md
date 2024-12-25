# Classification_and_processing_of_documents
This the official submission of the team 'Technarx' for the PS1 of the Appian AI Application Challenge 2025.

This is the pipeline flow:-


<img width="899" alt="Screenshot 2024-12-26 at 12 37 44 AM" src="https://github.com/user-attachments/assets/6c05df67-e7e3-4250-900e-acfda7551e31" />

We have used a fine tuned LayoutLM classification model, which based on a BERT model but further adds a 2d positional embedding. We have finetuned the model on a custon made data set (169 scanned pdf documents) which were of the following classes:- 'invoice', 'resume', 'passport', 'Tax_Statement', 'balance_sheet', 'Income_Statement', 'Driving_License'. 

We address edge cases where a document doesn't fit predefined labels by using an LLM to assign a label based on its text. A human-in-the-loop system verifies and adjusts the label if the model's confidence is below 95%, ensuring accuracy.

The name and address are extracted from the documents (or marked as "None" if absent) using few-shot learning with the Llama 3 LLM.

All the documents with their metadata are stored in a simple SQLite database. 

Run the app.py to launch the app on the browser.

This the interface:
<img width="884" alt="Screenshot 2024-12-26 at 1 12 52 AM" src="https://github.com/user-attachments/assets/316dea8d-d9d0-432f-a01b-497a48fcab67" />

Make sure u put valid file faths and api keys wherever needed.

download the needed requirements need in the requirements.txt.
