from flask import render_template
from flask import Flask
from model import db

def init_db():
    """ Initialize the database """
    db.create_all()


class _DefaultSettings(object):
    USERNAME = 'world'
    SECRET_KEY = 'development key'
    DEBUG = True

# create the application
app = Flask(__name__)
app.config.from_object(_DefaultSettings)
del _DefaultSettings

def init_db():
    """ Initialize the database """
    db.create_all()

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")
