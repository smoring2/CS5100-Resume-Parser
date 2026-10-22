import sys, fitz
import docx2txt

def read_pdf(file_path):
        file = open(file_path, "rb").read()
        doc = fitz.open("pdf", file)

        text = ""
        for page in doc:
            text = text + str(page.get_text())

        tx = " ".join(text.split('\n'))
        return tx

def read_txt(file_path):
        file = open(file_path, encoding="utf-8", errors="replace").read()
        # file = open(app.config['UPLOAD_FOLDER'] + filename).read().decode('utf-8')
        tx = ''
        for i in file:
           tx += str(i)
        return tx

def read_docx(file_path):
    file = docx2txt.process(file_path)

    text = "".join([s for s in file.splitlines(True) if s.strip("\r\n")])
    return text
