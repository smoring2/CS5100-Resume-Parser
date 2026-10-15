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
|      Python       | 3.13.x  |                                 Python programming language is being used in web development, Machine Learning applications, along with all cutting edge technology in the Software Industry.                                 |                                                                                                                                                                                             |
|       Flask       |  3.1.3  |                                                                                    Flask is a web application framework written in Python.                                                                                    |
|  spaCy(Package)   |  3.8.7  | spaCy is an open-source software library for advanced natural language processing. It features state-of-the-art speed and neural network models for tagging, parsing, named entity recognition, text classification and more. |
| pymupdf(Package)  | 1.25.5  |                               PyMuPDF adds Python bindings and abstractions to MuPDF, a lightweight PDF, XPS, and eBook viewer, renderer, and toolkit. It can be used to decrypt the document.                                |
| docx2txt(Package) |   0.9   |                                                                            A pure python-based utility to extract text and images from docx files.                                                                            |

## PEAS Environment

|  Agent Type   |                      Performance Measure                      |    Environment     |   Actuators    |                   Sensors                   |
|:-------------:|:-------------------------------------------------------------:|:------------------:|:--------------:|:-------------------------------------------:|
| Resume Parser | Parse resume’s contents into different categories accurately. | Internet, Computer | Screen display | Web pages, Resumes uploaded by users, Mouse |

## Install Dependencies
```
  python3.13 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
```

## Run In Terminal
```
  export FLASK_APP=app
  flask run --debug
```

