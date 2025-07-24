import os
from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient(os.environ['MONGODB_URI'])  # Get from Render env vars
db = client["user_auth"]

@app.route("/")
def home():
    return "Connected to MongoDB!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000
    app.run(host="0.0.0.0", port=port)
