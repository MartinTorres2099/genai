import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings import StableDiffusionEmbeddings  
# from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

def main():

  st.set_page_config(page_title="Ask your PDF")
  st.header("Ask your PDF 💬")

  # Upload PDF
  pdf = st.file_uploader("Upload PDF", type="pdf")

  # Extract pages from PDF
  if pdf is not None:
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
      text += page.extract_text()

    # Split text inot chunks  
    text_splitter = CharacterTextSplitter(
      separator="\n",
      chunk_size=1000,
      chunk_overlap=200,
      length_function=len
    )
    chunks = text_splitter.split_text(text)

    # embeddings = OpenAIEmbeddings()
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    knowledge_base = FAISS.from_texts(chunks, embeddings)

    user_question = st.text_input("Ask a question about your PDF:")
    
    if user_question:
      docs = knowledge_base.similarity_search(user_question)
      callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
      # llm = OpenAI() # Change to local llm
      # llm = LlamaCpp(model_path="./stable-vicuna-13B.ggml.q4_2.bin")
      llm = LlamaCpp(
        model_path="./stable-vicuna-13B.ggml.q4_2.bin",
        stop=["### Human:"],
        callback_manager=callback_manager,
        verbose=True,
        n_ctx=2048,
        n_batch=512
      )
      chain = load_qa_chain(llm, chain_type="stuff")
      response = chain.run(input_documents=docs, question=user_question)

      st.write(response)
      
if __name__ == "__main__":
  main()