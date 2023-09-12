import langchain
import streamlit as st
from langchain.llms import LlamaCpp
from langchain.chains import ConversationChain
from sentence_transformers import SentenceTransformer
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import pymongo
import re
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
import qdrant_client
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.text_splitter import CharacterTextSplitter

# Fix for some new weird "no attribute 'verbose'" bug https://github.com/hwchase17/langchain/issues/4164
langchain.verbose = False
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
client = pymongo.MongoClient()
db = client.pdf_db
# LLM setup
llm = LlamaCpp(
    model_path="./stable-vicuna-13B.ggml.q4_2.bin",
    callback_manager=callback_manager,
    verbose=True,
    n_ctx=2048,
    n_batch=512,
)

# Embeddings setup
model = SentenceTransformer('all-MiniLM-L6-v2')
# Create an empty dictionary to store embeddings
embeddings_dict = {
    'lm': model,  # Pass the SentenceTransformer model here for the language model
    'chain': llm, # Pass the LlamaCpp model here for the conversation chain
}

# SentenceTransformer setup
sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')

# ConversationChain Setup
conversation_chain =  llm

def generate_prompt(choice, name, dob):
    # Your generate_prompt function remains unchanged
    pass

def search(name, dob, pdfs):
    # Your search function remains unchanged
    pass

st.title("PDF Search Chatbot")
st.write("Enter name and DOB and click Search")

# Get input
name = st.text_input("Enter name:")
dob = st.text_input("Enter date of birth:")

if st.button("Search"):
    choice = st.selectbox("Choose style", ["Slow", "Medium", "Fast", "Superfast", "Default"])

    # Generate prompt
    generated_prompt = generate_prompt(choice, name, dob)

    # Use the LlamaCpp model to generate a response
    llm_response = "Sample LLM response"  # Replace with the actual response generation method you have

    # Use SentenceTransformer to embed the response
    llm_response_embedding = sentence_transformer_model.encode([llm_response])

    # Display the response and its embedding
    st.write("LLM Response:", llm_response)
    st.write("LLM Response Embedding:", llm_response_embedding)

    # Perform your search based on name and dob
    results = search(name, dob, db.pdfs.find())  # Pass the MongoDB cursor to search function

    if results:
        choice = st.selectbox("Choose summary style", ["Slow", "Medium", "Fast", "Superfast", "Default"])
        prompt = generate_prompt(choice, name, dob)
        summary = conversation_chain.predict(prompt)
        st.write(summary)
    else:
        st.write("No results found")
