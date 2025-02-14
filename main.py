from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Configuration (Make sure you set DATABASE_URL in your environment)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///stocks.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=10000.0)
    portfolio = db.relationship('Portfolio', backref='user', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials!")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists!")

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    portfolio = Portfolio.query.filter_by(user_id=user.id).all()
    return render_template("dashboard.html", user=user, portfolio=portfolio)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))

# API Route to Fetch Stock Price
@app.route("/get_stock/<symbol>")
def get_stock(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return jsonify({"symbol": symbol, "price": round(price, 2)})
    except:
        return jsonify({"error": "Invalid stock symbol"}), 400

# Buy Stock Route
@app.route("/buy", methods=["POST"])
def buy_stock():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    symbol = data.get("symbol").upper()
    quantity = int(data.get("quantity"))

    stock = yf.Ticker(symbol)
    try:
        price = stock.history(period="1d")["Close"].iloc[-1]
    except:
        return jsonify({"error": "Invalid stock symbol"}), 400

    total_cost = price * quantity
    user = User.query.get(session["user_id"])

    if user.balance < total_cost:
        return jsonify({"error": "Insufficient funds"}), 400

    existing_stock = Portfolio.query.filter_by(user_id=user.id, stock_symbol=symbol).first()
    if existing_stock:
        existing_stock.quantity += quantity
    else:
        new_stock = Portfolio(user_id=user.id, stock_symbol=symbol, quantity=quantity)
        db.session.add(new_stock)

    user.balance -= total_cost
    db.session.commit()

    return jsonify({"success": True, "balance": user.balance})

# Sell Stock Route
@app.route("/sell", methods=["POST"])
def sell_stock():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    symbol = data.get("symbol").upper()
    quantity = int(data.get("quantity"))

    user = User.query.get(session["user_id"])
    stock = Portfolio.query.filter_by(user_id=user.id, stock_symbol=symbol).first()

    if not stock or stock.quantity < quantity:
        return jsonify({"error": "Not enough stock owned"}), 400

    stock_price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
    earnings = stock_price * quantity
    user.balance += earnings

    if stock.quantity == quantity:
        db.session.delete(stock)
    else:
        stock.quantity -= quantity

    db.session.commit()
    return jsonify({"success": True, "balance": user.balance})

# Leaderboard Route
@app.route("/leaderboard")
def leaderboard():
    users = User.query.order_by(User.balance.desc()).all()
    return render_template("leaderboard.html", users=users)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)


from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

