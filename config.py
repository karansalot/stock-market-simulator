import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Fetch from environment variables
    SQLALCHEMY_TRACK_MODIFICATIONS = False
