import streamlit as st
import pymongo
from langchain.llms import OpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain import LlamaCpp

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["pdf_db"]
collection = db["pdf_collection"]

def main():
    st.set_page_config(page_title="Summarize PDFs")
    st.header("Summarize PDFs 📃")

    # User input for filtering PDFs
    suspect_name = st.text_input("Enter Suspect Name:")
    officer_name = st.text_input("Enter Officer Name:")
    date_of_arrest = st.text_input("Enter Date of Arrest:")

    # Check if any filter field has been filled
    if suspect_name or officer_name or date_of_arrest:
        # Query MongoDB for relevant PDF chunks
        query = {
            "extracted_headers.suspect_name": suspect_name.strip(),  # Adjust the field name and format
            "extracted_headers.officer_name": officer_name.strip(),  # Adjust the field name and format
            "extracted_headers.date_of_arrest": date_of_arrest.strip(),  # Adjust the field name and format
        }

        # Display the query for debugging
        st.write("Query:", query)

        # Try to retrieve a matching chunk using find_one()
        matching_chunk = collection.find_one(query)

        if matching_chunk is not None:
            st.write("Matching chunk found in the database:")
            st.write("Text Chunk:", matching_chunk.get("text_chunk", ""))
        else:
            st.write("No matching chunk found.")

        # Check if the MongoDB client is connected and authenticated
        if client is not None:
            st.write("MongoDB client is connected.")
            if db is not None:
                st.write(f"Using database: {db.name}")
                if collection is not None:
                    st.write(f"Using collection: {collection.name}")

                    # Print the database and collection names for debugging
                    st.write("Database Name:", db.name)
                    st.write("Collection Name:", collection.name)

                    # Collect matching chunks and get their count
                    matching_chunks = list(collection.find(query))
                    matching_count = len(matching_chunks)

                    if matching_count > 0:
                        st.write("Matching chunks found in the database:")
                        for chunk in matching_chunks:
                            st.write(chunk["text_chunk"])
                    else:
                        st.write("No matching chunks found.")
                else:
                    st.write("Collection is not specified.")
            else:
                st.write("Database is not specified.")
        else:
            st.write("MongoDB client is not connected.")

        # Load LLMS model
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        llm = LlamaCpp(
            model_path="./stable-vicuna-13B.ggml.q4_2.bin",
            stop=["### Human:"],
            callback_manager=callback_manager,
            verbose=True,
            n_ctx=2048,
            n_batch=512
        )
        chain = load_qa_chain(llm, chain_type="stuff")

        # Summarize relevant PDF chunks
        if matching_count > 0:
            for chunk in matching_chunks:
                knowledge_base = FAISS.deserialize(chunk["knowledge_base"])
                user_question = ""  # You can define a specific question here
                docs = knowledge_base.similarity_search(user_question)
                response = chain.run(input_documents=docs, question=user_question)

                st.write(f"Summary for Chunk from {chunk['file_name']}:\n")
                st.write(response)
        else:
            st.warning("No matching PDFs found.")
    else:
        st.write("Please enter at least one filter field to search for matching PDFs.")

if __name__ == "__main__":
    main()
