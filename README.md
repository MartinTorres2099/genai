# Hackathon Code - Document Ingestion With ChatBot

This code was written for a hackathon. The POC was as follows:
A front end website was built using streamlit to ingest the PDF documents.

The ingestion process used LangChain and a mondodb backend to save the vectorized data.

A second website was being built using streamlit was to be used to query the documents using prompt engineering,
returning data in 4 different ways:
* Media - summary of document searched
* Public - 8th to 12th grade reading level summary
* Clerks - 1 page summary, college level reading
* Judge - summarize but no change in reading level

Because this was a POC, a local LLM was loaded and used to save on API costs to LLM's available to the public.

The prompt engineering portion has not been implamented.

There is an abundance of code that was written. Some is for troubleshooting purposes,
other code was left as guide on how some aspect of the code worked and others did not.

The virtual environment and local LLM model were not uploaded to this repo.

## Setting up environment

The follwing steps were followed to build the environment to run the code:

##### Activate the virtual environment 
* call C:\git\hackathon2023\venv\Scripts\activate.bat

##### Start MonoDB (Open in new cli window)
* call C:\"Program Files"\MongoDB\Server\6.0\bin\mongod --port 27017 --dbpath C:\git\hackathon2023\db

##### Start tika server (Open in new window)
* call cd \
* call cd c:\tika
* call START /B java -jar tika-server-standard-2.8.0.jar --port 9998

##### Working code to import PDF file
* call streamlit run doc-proc-pdf-upload.py

##### Testing code to search and summarize PDF file
* call streamlit run doc-proc-pdf-summarize.py

##### Deactivate the virtual environment
* call C:\git\hackathon2023\venv\Scripts\deactivate.bat

##### Check PDF File - used for troublshooting code
* call python show_pdf.py

Development on this code has been paused for now. I may continue to work on it in the near future.
