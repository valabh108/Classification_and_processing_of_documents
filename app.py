import streamlit as st
import os
import sqlite3
from Predictor import predict
from Predictor import classes
import pandas as pd
from Name_Summary_Extract import name_extract, summary_extract

# Define the directory to save files
save_dir = "./uploaded_files"
os.makedirs(save_dir, exist_ok=True)

# Connect to the SQLite database
conn = sqlite3.connect("./uploaded_pdf_database1.db")
cursor = conn.cursor()

# Create a table for storing metadata (if it doesn't exist)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pdf_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename UNIQUE,
        filepath UNIQUE,
        classification_label TEXT,
        name TEXT,
        address TEXT,
        summary TEXT,
        upload_timestamp TEXT
    )
''')
conn.commit()

# Page Title
st.title("Appian Credit Union")

# Use columns to divide the page into two sections
col1, col2 = st.columns([20, 35])  # Adjust column width

# Left column: Database Section
# Left column: Database Section
with col2:
    st.write("### Database")

    # Search input and search type buttons
    col_search = st.columns([1])[0]
    search_query = st.text_input("Search files", value=st.session_state.get("search_query", ""), key="search_input")
    st.write('Search by:')
    col_buttons = st.columns([1, 1, 1, 1])  # Added an extra button
    if col_buttons[0].button("Filename"):
        st.session_state["search_type"] = "filename"
    if col_buttons[1].button("Type"):
        st.session_state["search_type"] = "classification_label"
    if col_buttons[2].button("Name"):  # Added the "Name" button
        st.session_state["search_type"] = "name"
    if col_buttons[3].button("Clear"):
        st.session_state["search_query"] = ""
        search_query = ""  # Reset search query
        st.session_state["search_type"] = None

    # Determine the search type
    search_type = st.session_state.get("search_type", "filename")

    if search_query:
        query = f"SELECT * FROM pdf_metadata WHERE {search_type} LIKE ?"
        cursor.execute(query, ('%' + search_query + '%',))
        results = cursor.fetchall()

        st.write(f"Search Results by {search_type.capitalize()}:")
        if results:
            # Convert the results into a pandas DataFrame for better visualization
            df_results = pd.DataFrame(results, columns=["id", "filename", "filepath", "classification Label", "name", "address", "summary", "Upload Timestamp"])
            st.dataframe(df_results, use_container_width=True)
        else:
            st.write("No files found.")
    else:
        st.write("No search query entered.")

    col_show, col_clear_db = st.columns([4, 1])

    with col_show:
        if st.button("Show Database"):
            # Fetch the entire database
            cursor.execute("SELECT * FROM pdf_metadata")
            all_data = cursor.fetchall()
            st.session_state["database_data"] = all_data

    with col_clear_db:
        if st.button("Clear", key="clear_database"):
            st.session_state["database_data"] = None

    if "database_data" in st.session_state and st.session_state["database_data"]:
        all_data = st.session_state["database_data"]
        if all_data:
            # Convert the data to a DataFrame for display
            df_all = pd.DataFrame(all_data, columns=["id", "filename", "filepath", "classification Label", "name", "address", "summary", "Upload Timestamp"])
            st.write("### Complete Database")
            st.dataframe(df_all, use_container_width=True, height=500)
        else:
            st.write("No records in the database.")

# Right column: File Uploader Section
with col1:
    st.write("### Upload New Files")
    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Save the uploaded file locally
            file_path = os.path.join(save_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Create the DataFrame with a proper structure
            data = {'file_path': [file_path]}  # Wrap file_path in a list to match DataFrame format
            df = pd.DataFrame(data)
            text, label, human_needed = predict(df)
            name, address = name_extract(text, label)
            summary = summary_extract(label, text)
            # Use session state to control popup visibility
            popup_key = f"show_popup_{uploaded_file.name}"
            if popup_key not in st.session_state:
                st.session_state[popup_key] = human_needed

            if st.session_state[popup_key]:
                st.warning(f"Human intervention required for file: {uploaded_file.name}")
                new_label = st.text_input(
                    "Verify or modify the classification label:",
                    value=label,
                    key=f"new_label_{uploaded_file.name}"
                )
                if st.button(f"Confirm {uploaded_file.name}"):
                    label = new_label
                    cursor.execute("SELECT * FROM pdf_metadata WHERE filepath = ?", (file_path,))
                    if cursor.fetchone():
                        st.warning(f"The file '{uploaded_file.name}' is already uploaded.")
                    else:
                        # Insert the metadata into the database
                        cursor.execute('''
                            INSERT INTO pdf_metadata (filename, filepath, classification_label, name, address, summary, upload_timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (uploaded_file.name, file_path, label, name, address, summary))
                        conn.commit()
                    st.session_state[popup_key] = False
                    st.success(f"File {uploaded_file.name} saved with label: {label}")
            else:
                cursor.execute("SELECT * FROM pdf_metadata WHERE filepath = ?", (file_path,))
                if cursor.fetchone():
                    st.warning(f"The file '{uploaded_file.name}' is already uploaded.")
                else:
                    # Insert the metadata into the database
                    cursor.execute('''
                        INSERT INTO pdf_metadata (filename, filepath, classification_label, name, address, summary, upload_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (uploaded_file.name, file_path, label, name, address, summary))
                    conn.commit()

            st.write(f"File saved to: {file_path}")
            st.write(f"Classification label: {label}")

# Close the database connection
conn.close()
