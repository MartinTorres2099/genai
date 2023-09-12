import re
import langchain
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient

client = MongoClient()
db = client.pdf_db

name_model = SentenceTransformer('all-MiniLM-L6-v2') 

def search_pdfs(first_name, last_name=None, dob=None):

  if last_name:
    docs = db.pdfs.find({'text': {'$regex': first_name + '.*' + last_name, '$options':'i'}})
  elif dob:
    docs = db.pdfs.find({'text': {'$regex': first_name + '.*' + dob, '$options':'i'}})
  
  if not docs:
    print("No matching documents found")
    return

  for doc in docs:
    text = doc['text']
    
    # Split text into chunks of 100 words
    chunks = langchain.chunk_text(text, chunk_size=100) 
    
    # Encode chunks into vectors
    chunk_embeddings = name_model.encode(chunks)
    
    # Summarize    
    summary = langchain.llm_summarize(chunks, chunk_embeddings)
    
    print(f"Match found in {doc['path']}")
    print(summary)
    
first_name = input("Enter first name: ")
last_name = input("Enter last name (or press Enter to skip): ")
dob = input("Enter date of birth (or press Enter to skip): ")

search_pdfs(first_name, last_name, dob)