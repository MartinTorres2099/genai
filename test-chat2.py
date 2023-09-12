import streamlit as st
from langchain.llms import LlamaCpp  
from langchain.chains import ChatChain
from langchain.embeddings import SentenceTransformerEmbeddings
import pymongo
import re

# Setup functions
def setup_langchain():
  llm = LlamaCpp(model_path="stable-vicuna-13B.ggml.q4_2.bin")
  embeddings = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")  
  return ChatChain(llm=llm, embeddings=embeddings, prompt="Act as a helpful chatbot")

def connect_db():
  client = pymongo.MongoClient()
  return client.pdf_db  

# Prompt engineering functions
def minimize_miscommunication(name, dob):
  # function body
  return f"Summarize the key information about {name} and their date of birth {dob} from these texts in a clear, concise way to minimize misinterpretation or the need for me to read the full text:"

def reading_level(name, dob, grade):
  # function body
  return f"Summarize the key information about {name} and their date of birth {dob} from these texts in a simple way for an {grade_level} grade reading level:"
  
def college_length(name, dob):
  # function body
  return f"Summarize the key information about {name} and their date of birth {dob} from these texts in a one page summary for a college reading level:" 

def default_prompt(name, dob):
  # function body
  return f"Summarize the key information about {name} and their date of birth {dob} from these texts:"

# Allow user to select prompt  
options = ["Minimize miscommunication", "8th-12th grade reading level", "1 page college reading level", "Default"]
choice = st.selectbox("Choose summary style", options)

if choice == options[0]:
  prompt = minimize_miscommunication(name, dob)
elif choice == options[1]:
  grade_level = st.number_input("Enter grade level:", min_value=8, max_value=12, value=10)
  prompt = reading_level(name, dob, grade_level)
elif choice == options[2]:
  prompt = college_length(name, dob)
else:
  prompt = default(name, dob)
  
# Generate summary
response = chatchain.predict(prompt)
  
# Create app
st.title("PDF Search Chatbot")

# Initialize
db = connect_db()
pdfs = db.pdfs.find() 
chatchain = setup_langchain()

# Get user input
name = st.text_input("Enter name:")
dob = st.text_input("Enter date of birth:")

# Search logic
if name and dob:

  results = search(name, dob, pdfs)
  
  if results:
    # Prompt engineering
    choice = st.selectbox("Choose summary style", options)
    prompt = select_prompt(choice, name, dob)
    
    # Summarize
    summary = chatchain.predict(prompt)
    
    st.write(summary)

  else:
    st.write("No results found")
    
else:
  st.write("Enter name and DOB to search")