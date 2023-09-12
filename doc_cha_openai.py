import os
import re
from langchain.llms import OpenAI
from pymongo import MongoClient
import PyPDF2

client = MongoClient()
db = client.pdf_database
summaries = db.summaries

openai = OpenAI(model_name="text-davinci-003")

first_name = input("Enter a first name: ")
query_by = input("Search by last name or date of birth? (name/dob): ")

if query_by == "name":
  last_name = input("Enter a last name: ")
  query = {"first_name": first_name, "last_name": last_name}
else:
  dob = input("Enter a date of birth (MM/DD/YYYY): ")
  query = {"first_name": first_name, "dob": dob}

pdf_dir = "/path/to/pdf/files"

for filename in os.listdir(pdf_dir):
  if filename.endswith(".pdf"):
    pdf_path = os.path.join(pdf_dir, filename)
    
    pdf = PyPDF2.PdfReader(pdf_path)
    
    text = ""
    
    for page in pdf.pages:
      text += page.extract_text()
    
    info = re.search(rf"{first_name}.*{query_by}.*({last_name}|{dob})", text, re.IGNORECASE)
    
    if info:
      print(f"Found match in {pdf_path}")
      
      summary = openai.complete("Summarize this text: " + text)
      
      document = {
        "filename": filename, 
        "text": text,
        "summary": summary['choices'][0]['text'],
        "query": query
      }
      
      summaries.insert_one(document)
      
print("Search complete!")