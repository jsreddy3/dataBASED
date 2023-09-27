from PyPDF2 import PdfFileReader
from docx import Document
from bs4 import BeautifulSoup

def convert_to_txt(file):
    extension = file.filename.rsplit('.', 1)[1].lower()

    if extension == 'pdf':
        return convert_pdf_to_txt(file)
    elif extension in ['doc', 'docx']:
        return convert_docx_to_txt(file)
    elif extension == 'html':
        return convert_html_to_txt(file)
    else:
        return ""

def convert_pdf_to_txt(file):
    pdf_reader = PdfFileReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extractText()
    return text

def convert_docx_to_txt(file):
    doc = Document(file)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

def convert_html_to_txt(file):
    soup = BeautifulSoup(file, 'lxml')
    for script in soup(["script", "style"]):
        script.extract()
    return soup.get_text()
