import os

from flask import Flask
from flask_cors import CORS

from paas.scripts.api import api_bp

from ..database import create_db_and_tables

create_db_and_tables()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhosts:5173"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

app.register_blueprint(api_bp)


if __name__ == '__main__':
    app.run()
