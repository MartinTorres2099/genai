This code was written for a hackathon. The POC was as follows:
A front end website was built using streamlit to ingest the PDF document.
The ingestion process used LangChain and a mondodb backend to save the vectorized data.
A second website built using streamlit was to be used to query the documents and using prompt engineering,
return data in 4 different ways:
Media - summary of document
Public - 8th to 12th grade summary
Clerks - 1 page summary, college level
Judge - summarize but not change reading level
Because this was a POC, a local LLM was loaded and used to save on API costs to LLM's available to the public.

The prompt engineering portion has not been implamented.

There is an abundance of code that was written. Some is for troubleshooting purposes,
other code was left as guide on how some aspect of the code worked and others did not.

The virtual environment and local LLM model were not uploaded to this repo.