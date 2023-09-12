import streamlit as st
from langchain.llms import LlamaCpp
from langchain.chains import ChatChain
from langchain.embeddings import OpenAIEmbeddings
import re

# Initialize LangChain 
llm = LlamaCpp(
        model_path="./stable-vicuna-13B.ggml.q4_2.bin",
        stop=["### Human:"],
        callback_manager=callback_manager,
        verbose=True,
        n_ctx=2048,
        n_batch=512,
    )
# Use https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 as embedding
# (downloaded automatically)
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
chatchain = ChatChain(llm=llm, embeddings=embeddings, prompt="Act as a helpful chatbot") 

# Load PDF database
import pymongo
client = pymongo.MongoClient()
db = client.pdf_db
pdfs = db.pdfs.find()

st.title("DocProc PDF Search Chatbot")

name = st.text_input("Enter a name:")
doa = st.text_input("Enter a Date of Arrest:")

if name or doa:
  query = ""
  if name:
    first, last = name.split()
    query += f"first name {first} last name {last}"
  if doa:
    query += f" date of arrest {doa}"
  
  # Search PDFs
  results = []
  for pdf in pdfs:
    text = pdf['text']
    # Code check
    print(text)
    if re.search(rf"\b{first}\b.*\b{last}\b", text, re.I) and re.search(rf"\b{doa}\b", text):
      results.append(pdf)

  # Generate summary  
  if results:
    prompt = f"Here is a summary of information about {name} and their date of birth {doa} based on these texts:"
    for i, pdf in enumerate(results[:5]):
      prompt += f"\nText {i+1}: {pdf['text'][:200]}..."
    prompt += "\nSummary:"
    response = chatchain.predict(prompt)
    st.write(response)
  else:
    st.write("No results found.")
    
else:
  st.write("Enter a name and date of birth to search")