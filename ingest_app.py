import streamlit as st
import tika
import os
from PyPDF2 import PdfReader
from pymongo import MongoClient
from tika import parser

# Database
client = MongoClient()
db = client.pdf_db

# Folder paths
save_folder = 'pdf_files' 

# Define get_folder() function
def get_folder(header):
  # Determine folder
  if 'Speech' in header:
    return 'Speech'
  elif 'Text' in header:
    return 'Text'  
  elif 'Audio' in header:
    return 'Audio'
  else:
    return 'Other'

pdf_text = None
file_path = None
folder = None

st.title("PDF Ingestor")

pdf = st.file_uploader("Upload a PDF")

if pdf:
  # Read PDF contents
  pdf_reader = PdfReader(pdf)
  num_pages = len(pdf_reader.pages )
  # Extract text 
  pdf_text = ""
  for page in range(num_pages):
    page_obj = pdf_reader.pages[page]
    pdf_text += page_obj.extract_text()
  # Get header
  header = pdf_text.split('\n')[0]

  # Error handling - see what header information it is extracting
  # print("Extracted header: ", header )

  # Get folder
  folder = get_folder(header)
  # Construct full path
  file_path = os.path.join(save_folder, folder, pdf.name)      

  if os.path.exists(file_path):
    st.error("File already exists! Please rename the file!")

  if not os.path.exists(save_folder):
    os.mkdir(save_folder)

  with open(file_path, 'wb') as f:
    f.write(pdf.getbuffer())

  db.pdfs.insert_one({
    'text': pdf_text,
    'path': file_path
  })

  st.success('PDF saved to {}'.format(file_path))
