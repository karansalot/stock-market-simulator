import os
import re
import traceback  # Import to capture errors
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

# Set SQLAlchemy Database URI
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
try:
    db = SQLAlchemy(app)
    print("✅ Database initialized successfully!")
except Exception as e:
    print("❌ Database initialization error:", str(e))
    print(traceback.format_exc())

# Home route for testing
@app.route("/")
def home():
    return "Stock Mar
import os
import re
import traceback  # Import to capture errors
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

# Set SQLAlchemy Database URI
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
try:
    db = SQLAlchemy(app)
    print("✅ Database initialized successfully!")
except Exception as e:
    print("❌ Database initialization error:", str(e))
    print(traceback.format_exc())

# Home route for testing
@app.route("/")
def home():
    return "Stock Mar
