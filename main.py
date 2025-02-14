import os
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Fetch DATABASE_URL from Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Debugging: Print the database URL in logs
print("Original DATABASE_URL:", DATABASE_URL)

# Ensure the URL exists before using
if DATABASE_URL:
    # Convert 'postgres://' to 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Debugging: Print the corrected database URL
    print("Updated DATABASE_URL:", DATABASE_URL)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
