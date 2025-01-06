# Classification_and_processing_of_documents
This the official submission of the team 'Technarx' for the PS1 of the Appian AI Application Challenge 2025.

This is the pipeline flow:-
<img width="985" alt="Screenshot 2025-01-06 at 3 12 37 PM" src="https://github.com/user-attachments/assets/435cdde8-3f51-4be6-8ba9-ce828ab04ddf" />
We have used a fine tuned LayoutLM classification model, which based on a BERT model but further adds a 2d positional embedding. We have finetuned the model on a custon made data set (169 scanned pdf documents) which were of the following classes:- 'invoice', 'resume', 'passport', 'Tax_Statement', 'balance_sheet', 'Income_Statement', 'Driving_License'. 

Thank you for clarifying! Here's a revised and concise version:

For edge cases without predefined labels, the LLM assigns a label based on text content, with human-in-the-loop validation for low-confidence cases (<95%). When a new document arrives, its similarity score is checked against previously validated documents using concatenated text (SBERT) and spatial (LayoutLM) embeddings, enabling automatic labeling for similar types. Edge cases are stored in a flagged database, and if enough similar documents accumulate, a new label is created, retraining the model for continuous learning and reducing manual effort.

The name and address are extracted from documents using few-shot learning with the Llama 3 LLM. Examples for few-shot learning are dynamically selected from the database metadata based on semantic similarity to the current input, ensuring accurate and context-aware extractions. If absent, fields are marked as "None."

All the documents with their metadata are stored in a simple SQLite database. 

Run the app.py to launch the app on the browser.

This the interface:
<img width="884" alt="Screenshot 2024-12-26 at 1 12 52 AM" src="https://github.com/user-attachments/assets/316dea8d-d9d0-432f-a01b-497a48fcab67" />

Make sure u put valid file faths and api keys wherever needed.

download the needed requirements need in the requirements.txt.
