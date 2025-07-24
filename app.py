from flask import Flask, render_template, request, redirect, session, send_file
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.utils import secure_filename
from urllib.parse import quote_plus
import base64
from io import BytesIO
import os

app = Flask(__name__)

# Fixed secret key (DO NOT expose this in public repos if used in production)
app.secret_key = os.urandom(24)

# MongoDB Atlas connection using environment variable or fallback
username = quote_plus("rshic14")
password = quote_plus("7WJ2QBIsL4bxZkW2")
uri = f"mongodb+srv://{username}:{password}@cluster0.cklkufm.mongodb.net/user_auth?retryWrites=true&w=majority&tls=true"
client = MongoClient(MONGO_URI)

db = client["user_auth"]
users_collection = db["users"]
images_collection = db["images"]

@app.route("/")
def index():
    if "user" in session:
        user = users_collection.find_one({"username": session["user"]})
        user_images = images_collection.find({"user_id": user["_id"]})
        return render_template("home.html", user=session["user"], images=user_images)
    return redirect("/login")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if users_collection.find_one({"email": email}):
            return "Email already exists!"

        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": password
        })
        return redirect("/login")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email, "password": password})
        if user:
            session["user"] = user["username"]
            return redirect("/")
        return "Invalid credentials!"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    file = request.files["image"]
    if not file:
        return "No file selected."

    filename = secure_filename(file.filename)
    file_data = file.read()

    user = users_collection.find_one({"username": session["user"]})

    images_collection.insert_one({
        "user_id": user["_id"],
        "filename": filename,
        "data": base64.b64encode(file_data).decode("utf-8"),
        "content_type": file.content_type
    })

    return redirect("/")

@app.route("/image/<image_id>")
def image(image_id):
    image_doc = images_collection.find_one({"_id": ObjectId(image_id)})
    if not image_doc:
        return "Image not found", 404

    return send_file(BytesIO(base64.b64decode(image_doc["data"])),
                     mimetype=image_doc["content_type"],
                     download_name=image_doc["filename"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
