import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ✅ Database Configuration (Ensure Environment Variable is Correct)
database_url = os.getenv("DATABASE_URL")
if database_url:
    database_url = database_url.replace("port", "5432")  # Fix incorrect port issue
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

db = SQLAlchemy(app)

# ✅ Serve HTML Templates
@app.route("/")
def home():
    return render_template("index.html")  # Ensure index.html is in the templates folder

@app.route("/about")
def about():
    return render_template("about.html")  # Ensure about.html is in the templates folder

@app.route("/contact")
def contact():
    return render_template("contact.html")  # Ensure contact.html is in the templates folder

# ✅ Database Connection Check
@app.route("/db-check")
def db_check():
    try:
        db.session.execute("SELECT 1")  # Simple test query
        return "✅ Database is connected!"
    except Exception as e:
        return f"❌ Database connection failed: {e}"

# ✅ Run Flask App (Ensure It Works on Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
