import streamlit as st
import os
import re
import pymongo
import numpy as np
from PyPDF2 import PdfReader
import faiss
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["pdf_db"]
collection = db["pdf_collection"]

# Folder paths
save_folder = 'pdf_files'

# Define a function to extract header fields dynamically
def extract_headers_and_values(text):
    headers = {}
    lines = text.split('\n')
    
    current_header = None  # Track the current header being processed

    for line in lines:
        if ':' in line:
            header, value = line.split(':', 1)
            header = header.strip()
            value = value.strip()

            if header == "date_of_arrest":
                # Extract date using regular expression
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', value)
                if date_match:
                    value = date_match.group()

            headers[header] = value
            current_header = header  # Set the current header

            st.write(f"Extracting {header}: {value}")

        elif current_header is not None:
            # If current_header is set, this line contains continuation of previous header
            headers[current_header] += ' ' + line.strip()
    
    return headers

# Define get_folder() function
def get_folder(header):
    folder_mappings = {
        'Suspect Name:': 'Arrest',
        'Citation of': 'Citation',
        'Incident Report': 'Incident',
    }
    for keyword, folder in folder_mappings.items():
        if keyword in header:
            return folder
    return 'Other'

def main():
    st.set_page_config(page_title="Upload and Save PDFs")
    st.header("Upload and Save PDFs 📄")

    # Upload PDF
    pdf = st.file_uploader("Upload PDF", type="pdf")

    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        st.write("Extracted Text:")  # Troubleshooting: Print extracted text
        st.write(text)

        header_info = text.split('\n', 1)[0] if '\n' in text else "Other"  # Extract first line as header
        extracted_headers = extract_headers_and_values(text)

        st.write("Extracted Headers and Values:")  # Troubleshooting: Print extracted headers and values
        for header, value in extracted_headers.items():
            st.write(f"{header}: {value}")

        # Define the file path for saving
        folder_name = get_folder(header_info)
        file_path = os.path.join(save_folder, folder_name, pdf.name)

        # Check for duplicate file
        if os.path.exists(file_path):
            st.error("File already exists! Please rename the file if you wish to import it.")
            return

        # Split text into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # Set the path to the downloaded SentenceTransformer model checkpoint
        model_path = "./all-MiniLM-L6-v2"
        model = SentenceTransformer(model_path)
        d = model.encode(['dummy']).shape[1]  # Get the embedding dimension
        # Create FAISS index
        index = faiss.IndexFlatIP(d)  # Index for inner product similarity

        # Store PDF chunks in MongoDB
        for chunk in chunks:
            # Encode chunk using SentenceTransformer model
            chunk_embedding = model.encode([chunk])[0]
            # Add chunk embedding to FAISS index
            chunk_embedding = np.array(chunk_embedding, dtype=np.float32)
            index.add(np.expand_dims(chunk_embedding, axis=0))

        # Save FAISS index to file
        os.makedirs(os.path.join(save_folder, folder_name), exist_ok=True)
        index_path = os.path.join(save_folder, folder_name, f'{pdf.name}.index')
        faiss.write_index(index, index_path)

        # Save PDF to appropriate folder
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(pdf.read())

        # Store PDF metadata in MongoDB
        pdf_data = {
            "file_name": pdf.name,
            "header_info": header_info,
            "extracted_headers": extracted_headers, 
            "index_path": index_path,
            "text_chunks": chunks,
        }

        collection.insert_one(pdf_data)

        # Add dynamically extracted headers and values to pdf_data
        # pdf_data.update(extracted_headers)

        # View extracted information
        st.subheader("Extracted Information from PDF:")
        for header, value in extracted_headers.items():
            st.write(f"{header}: {value}")
        st.write(f"Number of Chunks:", len(chunks)) 

        st.success('PDF uploaded, chunks saved to MongoDB, and files saved to {}'.format(file_path))

if __name__ == "__main__":
    main()
