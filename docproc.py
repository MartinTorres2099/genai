import os
import shutil
from pdf_parser import PDFParser
from private_gpt import PrivateGPT

# Set up the directories
pdfs_dir = 'PDFs'
output_dir = 'output'
incident_dir = 'incident'
#story_dir = 'story'
#speech_dir = 'speech'
not_found_dir = 'not found'

# Set up PrivateGPT
gpt = PrivateGPT('longchain.txt')

# Loop through each PDF file in the "PDFs" directory
for pdf_file in os.listdir(pdfs_dir):
    # Extract the suspect name, arresting officer, and date of arrest from the PDF file
    pdf_parser = PDFParser(open(os.path.join(pdfs_dir, pdf_file), 'rb'))
    suspect_name = pdf_parser.get_field('Suspect Name')
    arresting_officer = pdf_parser.get_field('Arresting Officer')
    date_of_arrest = pdf_parser.get_field('Date of Arrest')

    # Create a new file with the person's information
    person_file = open(os.path.join(output_dir, f'{suspect_name}{arresting_officer}{date_of_arrest}.txt'), 'w')
    person_file.write(f'{suspect_name} {arresting_officer}, arrested on {date_of_arrest}\n')
    person_file.close()

    # Query PrivateGPT for a match
    match = gpt.query(f'{suspect_name} {arresting_officer}')

    # If there's a match, ingest the file from the appropriate folder and summarize the content
    if match:
        file_path = os.path.join(match, pdf_file)
        summary = summarize(file_path)
        print(f'{suspect_name} {arresting_officer} - {summary}')

    # If there's no match, move the file to the "not found" directory
    else:
        shutil.move(os.path.join(output_dir, pdf_file), not_found_dir)