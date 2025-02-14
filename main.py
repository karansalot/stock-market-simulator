from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import yfinance as yf
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    cash = db.Column(db.Float, default=10000)
    stocks = db.Column(db.PickleType, default={})
    total_value = db.Column(db.Float, default=10000)  # Tracks net worth

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        return "Invalid login."
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            return "User already exists!"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/buy", methods=["POST"])
@login_required
def buy_stock():
    data = request.get_json()
    symbol = data["symbol"].upper()
    quantity = int(data["quantity"])
    
    stock = yf.Ticker(symbol)
    stock_data = stock.history(period="1d")

    if stock_data.empty:
        return jsonify({"error": "Invalid stock symbol."})

    price = stock_data["Close"].iloc[-1]
    cost = price * quantity

    if current_user.cash >= cost:
        current_user.cash -= cost
        current_user.stocks[symbol] = current_user.stocks.get(symbol, 0) + quantity
        db.session.commit()
        return jsonify({"success": True, "portfolio": {"cash": current_user.cash, "stocks": current_user.stocks}})
    else:
        return jsonify({"error": "Not enough cash!"})

@app.route("/sell", methods=["POST"])
@login_required
def sell_stock():
    data = request.get_json()
    symbol = data["symbol"].upper()
    quantity = int(data["quantity"])

    if current_user.stocks.get(symbol, 0) >= quantity:
        stock = yf.Ticker(symbol)
        stock_data = stock.history(period="1d")

        if stock_data.empty:
            return jsonify({"error": "Invalid stock symbol."})

        price = stock_data["Close"].iloc[-1]
        revenue = price * quantity

        current_user.cash += revenue
        current_user.stocks[symbol] -= quantity
        if current_user.stocks[symbol] == 0:
            del current_user.stocks[symbol]
        
        db.session.commit()
        return jsonify({"success": True, "portfolio": {"cash": current_user.cash, "stocks": current_user.stocks}})
    else:
        return jsonify({"error": "Not enough shares to sell!"})

@app.route("/leaderboard")
@login_required
def leaderboard():
    users = User.query.all()
    leaderboard_data = []
    
    for user in users:
        total_value = user.cash
        for stock, quantity in user.stocks.items():
            stock_data = yf.Ticker(stock).history(period="1d")
            if not stock_data.empty:
                total_value += stock_data["Close"].iloc[-1] * quantity
        
        percentage_gain = ((total_value - 10000) / 10000) * 100
        leaderboard_data.append({"username": user.username, "net_worth": total_value, "gain": round(percentage_gain, 2)})

    leaderboard_data.sort(key=lambda x: x["net_worth"], reverse=True)
    
    return render_template("leaderboard.html", leaderboard=leaderboard_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
