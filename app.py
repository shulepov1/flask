from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp_key'

from browsers_app import routes

