# flask run --host=0.0.0.0 --port=8000

from flask import Flask
app = Flask(__name__)
from app import app
