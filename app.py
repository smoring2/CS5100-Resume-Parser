import os
import tempfile
from uuid import uuid4
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import spacy
import random
from tabulate import tabulate
from prettytable import PrettyTable
import pathlib
from train_model import*
from read_file import*

app = Flask(__name__)

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "resume_parser_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

train_model()

nlp.to_disk('training_files/nlp_model')
nlp_model = spacy.load('training_files/nlp_model')

print("---------Model Training Done---------")

# Get test result
# print("---------Model Testing Report---------")
# test_model_report()


def _validate_magic_bytes(file_path, ext):
    """Verify that the file content matches the claimed extension via magic bytes."""
    with open(file_path, "rb") as fh:
        header = fh.read(8)

    if ext == ".pdf":
        return header[:5] == b"%PDF-"
    elif ext == ".docx":
        # DOCX files are ZIP archives starting with PK\x03\x04
        if header[:4] != b"PK\x03\x04":
            return False
        # Additionally verify the ZIP contains word/document.xml
        import zipfile
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                return "word/document.xml" in zf.namelist()
        except (zipfile.BadZipFile, Exception):
            return False
    elif ext == ".txt":
        # For .txt we just verify it is decodable as text
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                fh.read(1024)
            return True
        except (UnicodeDecodeError, ValueError):
            return False

    return False


@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/display', methods = ['GET', 'POST'])
def parse_resume():
    if request.method == 'POST':
        f = request.files['file']
        original_name = secure_filename(f.filename)
        ext = pathlib.Path(original_name).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            return "Unsupported file type. Allowed types: pdf, txt, docx.", 400

        # Generate a server-side unique filename to avoid collisions and name-based attacks
        safe_name = uuid4().hex + ext
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)

        try:
            f.save(file_path)

            # Validate magic bytes match the claimed extension
            if not _validate_magic_bytes(file_path, ext):
                os.remove(file_path)
                return "File content does not match the declared file type.", 400

            file_content = ''
            if ext == ".pdf":
                file_content = read_pdf(file_path)
            elif ext == ".txt":
                file_content = read_txt(file_path)
            elif ext == ".docx":
                file_content = read_docx(file_path)

            t = PrettyTable(['Catalog', 'Value'])
            doc = nlp_model(file_content)
            for ent in doc.ents:
                t.add_row([str(ent.label_.upper()), str(ent.text)])
        finally:
            # Always clean up the uploaded file after parsing
            if os.path.exists(file_path):
                os.remove(file_path)

    return render_template('content.html', content=t)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug = True)
