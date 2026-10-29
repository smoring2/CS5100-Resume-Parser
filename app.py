import logging
import os
import secrets
import tempfile

from flask import Flask, abort, render_template, request, session
from werkzeug.utils import secure_filename
import spacy
import random
from tabulate import tabulate
from prettytable import PrettyTable
import pathlib
from train_model import*
from read_file import*

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

# SECRET_KEY is required for session support and CSRF protection.
# In production set the APP_SECRET_KEY environment variable to a strong,
# persistent value.  A random fallback is generated so the app never runs
# without a key, but sessions will not survive restarts when using the
# fallback.
app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", secrets.token_hex(32))

app.config["UPLOAD_FOLDER"] = "static/"

# Limit upload size to 16 MB to prevent denial-of-service via large files.
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# Restrict uploads to known resume file extensions.
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

# ---------------------------------------------------------------------------
# API-key authentication
# ---------------------------------------------------------------------------
# Set the API_KEY environment variable to enforce token-based auth on every
# request.  When the variable is unset the app falls back to unauthenticated
# mode (see README.md § Authentication for the rationale and compensating
# guardrails that apply in that case).
API_KEY = os.environ.get("API_KEY")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model training (startup)
# ---------------------------------------------------------------------------
train_model()

nlp.to_disk('training_files/nlp_model')
nlp_model = spacy.load('training_files/nlp_model')

print("---------Model Training Done---------")

# Get test result
# print("---------Model Testing Report---------")
# test_model_report()


# ---------------------------------------------------------------------------
# Authentication hook
# ---------------------------------------------------------------------------
@app.before_request
def check_authentication():
    """Enforce API-key authentication when API_KEY is configured.

    Clients must supply the key in the ``Authorization`` header using the
    ``Bearer`` scheme, or as an ``api_key`` query parameter.

    When API_KEY is *not* set the hook is a no-op and the application runs
    in unauthenticated mode with compensating guardrails (see README.md).
    """
    if API_KEY is None:
        return  # unauthenticated mode – guardrails apply instead

    # Extract token from Authorization header or query parameter
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        token = request.args.get("api_key")

    if not token or not secrets.compare_digest(token, API_KEY):
        logger.warning(
            "Unauthenticated request blocked: %s %s from %s",
            request.method,
            request.path,
            request.remote_addr,
        )
        abort(401)


# ---------------------------------------------------------------------------
# Request logging
# ---------------------------------------------------------------------------
@app.after_request
def log_request(response):
    """Log every request for audit purposes."""
    logger.info(
        "%s %s %s %s %s",
        request.remote_addr,
        request.method,
        request.path,
        response.status_code,
        request.content_length or 0,
    )
    return response


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _allowed_file(filename: str) -> bool:
    """Return True if *filename* has an allowed extension."""
    return pathlib.Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/display', methods = ['GET', 'POST'])
def parse_resume():
    if request.method == 'POST':
        f = request.files.get('file')
        if f is None or f.filename == '':
            abort(400)

        file_name = secure_filename(f.filename)
        if not file_name or not _allowed_file(file_name):
            abort(400)

        file_extension = pathlib.Path(file_name).suffix.lower()

        # Write the upload to a temporary file so no user-controlled data
        # persists on the server filesystem after the request completes.
        tmp_dir = tempfile.mkdtemp()
        file_path = os.path.join(tmp_dir, file_name)
        try:
            f.save(file_path)

            file_content = ''
            if file_extension == ".pdf":
                file_content = read_pdf(file_path)
            elif file_extension == ".txt":
                file_content = read_txt(file_path)
            elif file_extension == ".docx":
                file_content = read_docx(file_path)

            t = PrettyTable(['Catalog', 'Value'])
            doc = nlp_model(file_content)
            for ent in doc.ents:
                t.add_row([str(ent.label_.upper()), str(ent.text)])
        finally:
            # Clean up: remove the uploaded file immediately after parsing
            # so no PII accumulates on disk behind an open endpoint.
            try:
                os.remove(file_path)
                os.rmdir(tmp_dir)
            except OSError:
                logger.exception("Failed to clean up temporary upload %s", file_path)

    return render_template('content.html', content=t)

if __name__ == '__main__':
    # Bind to localhost only by default.  Set HOST=0.0.0.0 explicitly in
    # production behind an authenticating reverse-proxy if external access
    # is needed.  Debug mode is disabled by default; set FLASK_DEBUG=1 to
    # enable during local development only.
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
