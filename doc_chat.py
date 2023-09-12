import os
import re
import PyPDF2
import qdrant_client
from langchain import LLMChain, LlamaCpp
from langchain.text_splitter import CharacterTextSplitter
from pymongo import MongoClient 
from os.path import join
from langchain.vectorstores import Qdrant
from langchain.embeddings import SentenceTransformerEmbeddings
from qdrant_client import QdrantClient

client = MongoClient()
db = client.pdf_database
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
llm = LlamaCpp(model_path="./stable-vicuna-13B.ggml.q4_2.bin")
qdrant_client =  QdrantClient(path="./db/") 
vectorstore = Qdrant(
    client=qdrant_client,
    collection_name="doc_chunks",
    embedding_function=embeddings.embed_query
)

pdf_dir = "pdf_files"

for root, dirs, files in os.walk(pdf_dir):
  for filename in files:
    if filename.endswith(".pdf"):
        pdf_path = join(root, filename)  
    
        pdf = PyPDF2.PdfReader(pdf_path)
    
        text = ""
    
        for page in pdf.pages:
            text += page.extract_text()

        text_splitter = CharacterTextSplitter(
            separator="\n", 
            chunk_size=1000, 
            chunk_overlap=200, 
            length_function=len
        )

        chunks = text_splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            qdrant_client.upsert(f"pdf_chunk_{filename}_{i}", chunk)

first_name = input("Enter a first name: ")
query_by = input("Search by last name or date of birth? (name/dob): ")

if query_by == "name":
  last_name = input("Enter a last name: ")
  query = {"first_name": first_name, "last_name": last_name}
else:
  dob = input("Enter a date of birth (MM/DD/YYYY): ")
  query = {"first_name": first_name, "dob": dob}

# Retrieve chunks to search 
chunks = []
for i in range(len(chunks)):
  chunk = vectorstore.query(f"pdf_chunk_{filename}_{i}")
  chunks.append(chunk)

full_text = " ".join(chunks) 

# Name search
if query_by == "name":

  regex = rf"{first_name}.*{last_name}"
  
  info = re.search(regex, full_text, re.IGNORECASE)

  print(f"Retrieved {len(chunks)} chunks")

# DOB search
else:

  regex = rf"{first_name}.*{dob}"

  info = re.search(regex, full_text, re.IGNORECASE)

  print(f"Retrieved {len(chunks)} chunks")

if info:
  print(f"Found match in {pdf_path}")
  print(info.group(0))
  summary = llm.generate("Summarize this text: " + full_text)
  
  print(summary)
else:
  print("No match found.")
  
print("Search complete!")