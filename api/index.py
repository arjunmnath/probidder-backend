import os
from flask import Flask
from routes import appbp
from models import create_tables

app = Flask(__name__)

# Set configurations
app.config['DB_URI'] = os.environ.get('DB_URI')
app.config['SECRET_KEY'] = os.urandom(24)

try:
    with app.app_context():
        app.register_blueprint(appbp)

        # Create tables manually using the function
        create_tables()

except Exception as e:
    print(f"An error occurred: {e}")
