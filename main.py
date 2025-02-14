import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import yfinance as yf
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # Allow frontend to access backend

# 🔹 Configure Database (Render PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")  # Fix Render DB URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "your_secret_key"  # For user sessions

db = SQLAlchemy(app)

# 🔹 Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=10000)  # Default $10,000 starting cash

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# 🔹 Fetch Real-Time Stock Price
@app.route("/get_stock/<symbol>")
def get_stock(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    
    if data.empty:
        return jsonify({"error": "Invalid stock symbol"})
    
    return jsonify({"symbol": symbol, "price": round(data['Close'][0], 2)})

# 🔹 User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    
    if user and check_password_hash(user.password, data["password"]):
        session["user_id"] = user.id
        return jsonify({"message": "Login successful", "username": user.username, "balance": user.balance})
    
    return jsonify({"error": "Invalid credentials"}), 401

# 🔹 User Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_password = generate_password_hash(data["password"])
    
    new_user = User(username=data["username"], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"})

# 🔹 Buy Stocks
@app.route("/buy", methods=["POST"])
def buy_stock():
    data = request.json
    user = User.query.get(session["user_id"])
    
    stock_data = get_stock(data["symbol"]).json
    if "error" in stock_data:
        return jsonify({"error": "Invalid stock symbol"}), 400
    
    total_price = stock_data["price"] * int(data["quantity"])
    if user.balance < total_price:
        return jsonify({"error": "Insufficient balance"}), 400
    
    user.balance -= total_price
    portfolio = Portfolio.query.filter_by(user_id=user.id, stock_symbol=data["symbol"]).first()
    
    if portfolio:
        portfolio.quantity += int(data["quantity"])
    else:
        new_stock = Portfolio(user_id=user.id, stock_symbol=data["symbol"], quantity=int(data["quantity"]))
        db.session.add(new_stock)
    
    db.session.commit()
    return jsonify({"message": "Stock purchased successfully", "balance": user.balance})

# 🔹 Sell Stocks
@app.route("/sell", methods=["POST"])
def sell_stock():
    data = request.json
    user = User.query.get(session["user_id"])
    
    stock_data = get_stock(data["symbol"]).json
    if "error" in stock_data:
        return jsonify({"error": "Invalid stock symbol"}), 400
    
    portfolio = Portfolio.query.filter_by(user_id=user.id, stock_symbol=data["symbol"]).first()
    if not portfolio or portfolio.quantity < int(data["quantity"]):
        return jsonify({"error": "Not enough stocks to sell"}), 400
    
    portfolio.quantity -= int(data["quantity"])
    user.balance += stock_data["price"] * int(data["quantity"])
    
    if portfolio.quantity == 0:
        db.session.delete(portfolio)
    
    db.session.commit()
    return jsonify({"message": "Stock sold successfully", "balance": user.balance})

if __name__ == "__main__":
    app.run(debug=True)
