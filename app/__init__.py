from flask import Flask
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production

    from .auth import auth
    app.register_blueprint(auth)
    
    return app