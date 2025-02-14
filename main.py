import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Debugging: Print database URL to check if it's correct
database_url = os.getenv("DATABASE_URL")
print("Original DATABASE_URL:", database_url)  # This helps us see if the URL is correct

# Replace incorrect "port" with the correct PostgreSQL port (5432)
if database_url:
    database_url = database_url.replace("port", "5432")  # Fix the error

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

db = SQLAlchemy(app)

@app.route("/")
def home():
    return "Hello, Flask is running with a fixed database URL!"

if __name__ == "__main__":
    app.run(debug=True)
