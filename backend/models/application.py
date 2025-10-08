import os
from dotenv import load_dotenv
from flask import Flask

from .db import db

from .users import User
from .characters import Character

# Define project root path relative to current file to find templates
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#if frontend is applied:
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'templates')
# app = Flask(__name__, template_folder=TEMPLATE_DIR)


def create_app():
    """
    Configurates the Flask App
    :return:
    """

    # Initialize Flask app
    app = Flask(__name__, root_path=PROJECT_ROOT)

    # Secret key for flash
    load_dotenv()
    app.secret_key = os.getenv('SECRET_KEY')

    # Define dir for database
    current_dir = os.path.abspath(os.path.dirname(__file__))
    basedir =os.path.dirname(current_dir)
    db_path = os.path.join(basedir, 'data', 'story_database.sqlite')

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database with Flask
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()

    return app