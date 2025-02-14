import os
import json
import yfinance as yf
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Database Config (Render PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    cash = db.Column(db.Float, default=10000)
    portfolio = db.Column(db.Text, default=json.dumps({}))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            return "User already exists!"
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        return "Invalid credentials!"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/get_stock/<symbol>")
def get_stock(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    if data.empty:
        return jsonify({"error": "Stock not found"}), 404
    return jsonify({"symbol": symbol, "price": round(data['Close'].iloc[-1], 2)})

@app.route("/buy", methods=["POST"])
@login_required
def buy_stock():
    data = request.json
    symbol = data["symbol"]
    quantity = int(data["quantity"])
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    total_cost = quantity * price

    if current_user.cash >= total_cost:
        portfolio = json.loads(current_user.portfolio)
        if symbol in portfolio:
            portfolio[symbol] += quantity
        else:
            portfolio[symbol] = quantity

        current_user.cash -= total_cost
        current_user.portfolio = json.dumps(portfolio)
        db.session.commit()
        return jsonify({"success": True, "portfolio": portfolio, "cash": current_user.cash})
    
    return jsonify({"error": "Not enough funds"}), 400

@app.route("/sell", methods=["POST"])
@login_required
def sell_stock():
    data = request.json
    symbol = data["symbol"]
    quantity = int(data["quantity"])
    portfolio = json.loads(current_user.portfolio)

    if symbol in portfolio and portfolio[symbol] >= quantity:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        total_earnings = quantity * price

        portfolio[symbol] -= quantity
        if portfolio[symbol] == 0:
            del portfolio[symbol]

        current_user.cash += total_earnings
        current_user.portfolio = json.dumps(portfolio)
        db.session.commit()
        return jsonify({"success": True, "portfolio": portfolio, "cash": current_user.cash})
    
    return jsonify({"error": "Not enough shares"}), 400

@app.route("/leaderboard")
def leaderboard():
    users = User.query.order_by(User.cash.desc()).all()
    leaderboard_data = [{"username": user.username, "cash": user.cash} for user in users]
    return render_template("leaderboard.html", leaderboard=leaderboard_data)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
