"""
PDF search and summarization chatbot

Main app flow:

1. Setup database connection and LangChain
2. Get user input for name and DOB  
3. Search PDFs for matches
4. Select prompt based on user choice 
5. Generate summary with LangChain
6. Display summary to user
"""
import langchain
import streamlit as st
from langchain.llms import LlamaCpp
from langchain.chains import ConversationChain
# from langchain.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import pdfplumber
import pymongo
import re
import os

# Fix for some new weird "no attribute 'verbose'" bug https://github.com/hwchase17/langchain/issues/4164
langchain.verbose = False
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
client = pymongo.MongoClient()
db = client.pdf_db

def get_all_pdf_files(pdf_dir):

  pdf_files = []
  
  for root, dirs, files in os.walk(pdf_dir):
    for name in files:
      if name.endswith('.pdf'):
        pdf_files.append(os.path.join(root, name))

  return pdf_files

pdf_files = get_all_pdf_files('pdf_files')
pdfs = [pdfplumber.open(f) for f in pdf_files]
pdf_texts = [pdf.pages[0].extract_text() for pdf in pdfs] 
# embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
model = SentenceTransformer('all-MiniLM-L6-v2')
# Get embeddings 
# pdf_embeddings = embeddings.encode(pdf_texts)
# embeddings = model.encode(pdf_texts) 
embeddings = {}
for i, text in enumerate(pdf_texts):
  # embeddings[text] = embeddings[i]
  embeddings[text] = model.encode([text])[0]
# Create dictionary
embeddings_dict = {}
for i, text in enumerate(pdf_texts):
  # embeddings_dict[text] = pdf_embeddings[i]
  embeddings_dict[text] = embeddings[i]
llm = LlamaCpp(
  model_path="./stable-vicuna-13B.ggml.q4_2.bin",
  # stop=["### Human:"],
  callback_manager=callback_manager,
  verbose=True,
  n_ctx=2048,
  n_batch=512,
)
# Pass to ConversationChain 
conversation_chain = ConversationChain(
  embeddings=embeddings_dict,
  llm=llm
)

def generate_prompt(choice, name, dob):
  if choice == "Slow":
    return f"Summarize the key information about {name} and their date of birth {dob} from these texts in a clear, concise way to minimize misinterpretation or the need for me to read the full text:"

  elif choice == "Medium":
    grade = st.number_input("Enter grade level:", min_value=8, max_value=12, value=10)
    return f"Summarize the key information about {name} and their date of birth {dob} from these texts in a simple way for an {grade} grade reading level:"
  
  elif choice == "Fast":
     return f"Summarize the key information about {name} and their date of birth {dob} from these texts in a one page summary for a college reading level:"

  elif choice == "Superfast":
    return f"Summarize the key information about {name} and their date of birth {dob} from these texts:"

  else:
    return f"Summarize the key information about {name} and their date of birth {dob} from these texts in a clear, concise way to minimize misinterpretation or the need for me to read the full text:"

def search(name, dob, pdfs):
  results = []
  
  for pdf in pdfs:
    text = pdf["text"]
    
    if re.search(name, text) and re.search(dob, text):
      results.append(pdf)
      
  return results

st.title("PDF Search Chatbot")
st.write("Enter name and DOB and click Search")
# Get input
name = st.text_input("Enter name:")  
dob = st.text_input("Enter date of birth:")

if st.button("Search"):

  choice = st.selectbox("Choose style", ["Slow", "Medium", "Fast", "Superfast", "Default"]) 

  # Generate prompt
  generated_prompt = generate_prompt(choice, name, dob)

  # Pass to predict
  summary = conversation_chain.predict(generated_prompt)

  results = search(name, dob)

  if results:
    choice = st.selectbox("Choose summary style", ["Slow", "Medium", "Fast", "Superfast", "Default"])
    prompt = generate_prompt(choice, name, dob)
    summary = conversation_chain.predict(prompt)
    st.write(summary)

  else:
    st.write("No results found")
