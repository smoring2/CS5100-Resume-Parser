import logging
import os

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

app.config["UPLOAD_FOLDER"] = "static/"

train_model()

nlp.to_disk('training_files/nlp_model')
nlp_model = spacy.load('training_files/nlp_model')

print("---------Model Training Done---------")

# Get test result
# print("---------Model Testing Report---------")
# test_model_report()


@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler that returns a generic error page without leaking internals."""
    app.logger.error("Unhandled exception: %s", e)
    return render_template('error.html'), 500


@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/display', methods = ['POST'])
def parse_resume():
    try:
        if 'file' not in request.files:
            return render_template('error.html', message="No file uploaded. Please select a file."), 400

        f = request.files['file']
        if f.filename == '':
            return render_template('error.html', message="No file selected. Please select a file."), 400

        file_name = secure_filename(f.filename)
        file_path = app.config['UPLOAD_FOLDER'] + file_name
        f.save(file_path)
        file_extension = pathlib.Path(file_path).suffix

        file_content = ''
        try:
            if file_extension == ".pdf":
                file_content = read_pdf(file_path)
            elif file_extension == ".txt":
                file_content = read_txt(file_path)
            elif file_extension == ".docx":
                file_content = read_docx(file_path)
            else:
                return render_template('error.html', message="Unsupported file format. Please upload a PDF, TXT, or DOCX file."), 400
        except Exception:
            app.logger.error("Failed to read uploaded file: %s", file_name)
            return render_template('error.html', message="Unable to read the uploaded file. Please ensure it is a valid PDF, TXT, or DOCX file."), 400

        t = PrettyTable(['Catalog', 'Value'])
        doc = nlp_model(file_content)
        for ent in doc.ents:
            t.add_row([str(ent.label_.upper()), str(ent.text)])

        return render_template('content.html', content=t)

    except Exception:
        app.logger.error("Unexpected error processing resume upload")
        return render_template('error.html', message="An unexpected error occurred. Please try again."), 500

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1', 'yes')
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)
