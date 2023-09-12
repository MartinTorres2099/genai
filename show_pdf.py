import PyPDF2
import re

pdf_file = "example.pdf"

print(f"Loading PDF: {pdf_file}")

try:
  pdf = PyPDF2.PdfReader(pdf_file)
except Exception as e:
  print(f"Error loading PDF: {e}")
  exit()

print(f"PDF loaded successfully, pages: {len(pdf.pages)}")  

fields = {}

# Search text of each page for key value pairs
for i, page in enumerate(pdf.pages):

  print(f"Extracting text from page: {i+1}")

  try:
    text = page.extract_text()
  except:
    print(f"Error extracting text from page {i+1}")
    continue
  
  print(f"Text extracted from page {i+1}, length: {len(text)}")

  # Search for key value pairs
  matches = re.findall(r'(.*?): (.*)', text)
  
  print(f"Found {len(matches)} matches on page {i+1}")

  for match in matches:
    key = match[0]
    value = match[1]
  
    # Add to fields dict
    if key not in fields:
      fields[key] = value

# Print fields
print("\nFields found:")
if not fields:
  print("No fields found")
else:
  for key, value in fields.items():
    print(f"{key}: {value}")
  
# Display fields onscreen
from tkinter import *

root = Tk()

for i, page in enumerate(pdf.pages):

  text = page.extract_text()
  
  label = Label(root, text=text, wraplength=600)
  label.grid(row=i, column=0, padx=10, pady=10)

root.title("PDF Contents")
root.geometry("800x800") # Set window size
root.mainloop()