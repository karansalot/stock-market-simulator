import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
database_url = os.getenv("DATABASE_URL")
if database_url:
    database_url = database_url.replace("port", "5432")  # Ensure correct port
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

db = SQLAlchemy(app)

# Define a simple route to check if the server is running
@app.route("/")
def home():
    return "Hello, Flask is running successfully!"

# Database connection check
@app.route("/db-check")
def db_check():
    try:
        db.session.execute("SELECT 1")  # Simple test query
        return "✅ Database is connected!"
    except Exception as e:
        return f"❌ Database connection failed: {e}"

# Ensure the app runs correctly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
