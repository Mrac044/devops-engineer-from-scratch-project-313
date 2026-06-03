import os

from flask import Flask
from flask_cors import CORS

from ..database import create_db_and_tables
from .API import init_routes

create_db_and_tables()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhosts:5173"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

init_routes(app)


if __name__ == '__main__':
    app.run()
