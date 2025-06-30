from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    
    load_dotenv()
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

    from .routes import main
    app.register_blueprint(main)

    return app
