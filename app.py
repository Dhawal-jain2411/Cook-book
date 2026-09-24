from flask import Flask, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# 1. Load the secret variables from your .env file
load_dotenv()

# 2. Initialize the Flask application
app = Flask(__name__)

# 3. Connect to MongoDB using the URI from your .env file
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["cookbook_db"] # This names your database "cookbook_db"
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print("❌ Failed to connect to MongoDB:", e)

# 4. Create the route for the homepage
@app.route("/")
def home():
    # This tells Flask to look inside the "templates" folder for index.html
    return render_template("index.html")

# 5. Start the server
if __name__ == "__main__":
    app.run(debug=True)