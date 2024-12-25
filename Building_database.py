import sqlite3
import os

# Connect to SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect("./uploaded_pdf_database1.db")
cursor = conn.cursor()

# Create a table for storing metadata (if it doesn't exist)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pdf_metadata (gitt
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filepath TEXT,
        classification_label TEXT,
        name TEXT,
        address TEXT,
        summary TEXT,
        upload_timestamp TEXT
    )
''')
conn.commit()  # Commit to ensure table creation is saved

# Define the directory to save files
save_dir = "./uploaded_files"
os.makedirs(save_dir, exist_ok=True)


# Function to insert file metadata into the database
def insert_file_metadata(filename, filepath, label, name, address, summary):
    try:
        # Check if file already exists in the database
        cursor.execute('''
            SELECT * FROM pdf_metadata WHERE filename = ? AND filepath = ?
        ''', (filename, filepath))
        existing_file = cursor.fetchone()

        if existing_file:
            print(f"File {filename} already exists in the database.")
        else:
            # Insert file metadata into the database
            cursor.execute('''
                INSERT INTO pdf_metadata (filename, filepath, classification_label, name, address, summary, upload_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (filename, filepath, label, name, address, summary))
            conn.commit()  # Ensure changes are committed
            print(f"Metadata inserted for file: {filename}")
    except Exception as e:
        print(f"Error inserting metadata for {filename}: {e}")


# Get all the files in the folder
uploaded_files = os.listdir(save_dir)

# Process the files
for uploaded_file in uploaded_files:
    file_path = os.path.join(save_dir, uploaded_file)

    # Dummy values for metadata fields
    classification_label = "dummy_label"  # Replace with actual classification logic
    name = "name"  # Replace with extracted or provided name
    address = "dummy address"  # Replace with extracted or provided address
    summary = "dummy summary."  # Replace with extracted or provided summary

    # Insert metadata into the database
    insert_file_metadata(uploaded_file, file_path, classification_label, name, address, summary)

# Check the database entries to verify data was inserted
cursor.execute('SELECT * FROM pdf_metadata')
data = cursor.fetchall()

if data:
    print("Database entries:")
    for entry in data:
        print(entry)
else:
    print("No data found in the database.")

# Close the database connection
conn.close()
