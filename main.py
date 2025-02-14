import os
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Fetch the PostgreSQL database URL from Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix the database URL format for SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Set the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
