@app.route("/db-check")
def db_check():
    try:
        db.session.execute("SELECT 1")  # Run a simple query
        return "✅ Database is connected!"
    except Exception as e:
        return f"❌ Database connection failed: {e}"
