# CS5100-Resume-Parser

<!-- ABOUT THE PROJECT -->
## About The Project
This app can parse a resume into a structured format with the information needed. 
It will significantly improve the user's efficiency in processing resumes.

![](https://i.ibb.co/0yDZrT0/picture-1.png)
![](https://i.ibb.co/rMz4WNV/picture-2.png)

## Targeted Environment
The project mainly uses Python to deal with resume parsing logic and takes Flask framework, HTML language to build the web application.

|                   | Version |                                                                                                         Introduction                                                                                                          |
|:-----------------:|:-------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|      Python       | 3.9.13  |                                 Python programming language is being used in web development, Machine Learning applications, along with all cutting edge technology in the Software Industry.                                 |                                                                                                                                                                                             |
|       Flask       |  1.1.2  |                                                                                    Flask is a web application framework written in Python.                                                                                    |
|  spaCy(Package)   |  2.3.8  | spaCy is an open-source software library for advanced natural language processing. It features state-of-the-art speed and neural network models for tagging, parsing, named entity recognition, text classification and more. |
| pymupdf(Package)  | 1.21.0  |                               PyMuPDF adds Python bindings and abstractions to MuPDF, a lightweight PDF, XPS, and eBook viewer, renderer, and toolkit. It can be used to decrypt the document.                                |
| docx2txt(Package) |   0.8   |                                                                            A pure python-based utility to extract text and images from docx files.                                                                            |

## PEAS Environment

|  Agent Type   |                      Performance Measure                      |    Environment     |   Actuators    |                   Sensors                   |
|:-------------:|:-------------------------------------------------------------:|:------------------:|:--------------:|:-------------------------------------------:|
| Resume Parser | Parse resume's contents into different categories accurately. | Internet, Computer | Screen display | Web pages, Resumes uploaded by users, Mouse |

## Authentication

The application supports API-key authentication to protect all routes.

### Enabling authentication (recommended for any networked deployment)

Set the `API_KEY` environment variable before starting the server:

```bash
export API_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

Clients authenticate by including the key as a Bearer token:

```
Authorization: Bearer <your-api-key>
```

Or as a query parameter (less preferred):

```
GET /?api_key=<your-api-key>
```

Unauthenticated requests receive a `401 Unauthorized` response when `API_KEY` is set.

### Unauthenticated mode (development only)

When `API_KEY` is **not** set the application runs without authentication.
This mode is intended **only for local development** on a trusted network.

**Justification:** during local development the server binds to `127.0.0.1`
by default and is not reachable from external networks. Uploaded files are
written to a temporary directory and deleted immediately after parsing, so
no personal data accumulates on disk.

The following compensating guardrails are active regardless of
authentication mode:

| Guardrail | Detail |
|---|---|
| **Upload size limit** | `MAX_CONTENT_LENGTH` is set to 16 MB. Requests exceeding this are rejected. |
| **File-type allowlist** | Only `.pdf`, `.txt`, and `.docx` extensions are accepted. |
| **Temporary storage with cleanup** | Uploaded files are saved to a temporary directory and deleted immediately after parsing completes, even if an error occurs. |
| **Request logging** | Every request is logged with remote address, method, path, status code, and content length for audit purposes. |
| **No debug mode by default** | The debug console/traceback is disabled unless `FLASK_DEBUG=1` is explicitly set. |
| **Localhost binding** | The development server binds to `127.0.0.1` by default. Set `HOST=0.0.0.0` only behind an authenticating reverse proxy. |
| **Secret key** | A `SECRET_KEY` is always set (from `APP_SECRET_KEY` env var or a random fallback) so Flask sessions are cryptographically signed. |

> **For any Internet-facing deployment** you must set `API_KEY`, use a
> production WSGI server (e.g. gunicorn), and place the application behind
> an authenticating reverse proxy with TLS termination.

## Run In Terminal

### Local development (unauthenticated, localhost only)
```
export FLASK_APP=app
python app.py
```

### With authentication enabled
```
export FLASK_APP=app
export APP_SECRET_KEY="<a-strong-persistent-secret>"
export API_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
python app.py
```

### Environment variables reference

| Variable | Required | Description |
|---|---|---|
| `APP_SECRET_KEY` | Recommended | Flask secret key for session signing. A random key is generated if unset. |
| `API_KEY` | Recommended | When set, all routes require this token via `Authorization: Bearer` header or `api_key` query parameter. |
| `HOST` | No | Bind address. Defaults to `127.0.0.1`. |
| `PORT` | No | Bind port. Defaults to `5000`. |
| `FLASK_DEBUG` | No | Set to `1` to enable debug mode. Defaults to off. |
