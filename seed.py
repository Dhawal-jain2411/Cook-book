from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

client = MongoClient(
    os.getenv("MONGO_URI"),
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True
)
db = client["cookbook_db"]
recipes = db["recipes"]

recipes.delete_many({})

sample_data = [
    {
        "title": "Midnight Masala Maggi",
        "image_url": "https://images.unsplash.com/photo-1612929633738-8fe01f7c8166?w=500",
        "time_minutes": 5,
        "difficulty": "Easy",
        "tag": "Midnight Snack",
        "author": "admin",
        "ingredients": ["maggi", "water", "masala powder", "cheese", "butter"],
        "instructions": "1. Boil 2 cups of water.\n2. Break Maggi noodles into the water.\n3. Stir in the tastemaker masala.\n4. Cook for 2 mins until water absorbs.\n5. Top with a slice of cheese and let it melt."
    },
    {
        "title": "Peanut Butter Banana Toast",
        "image_url": "https://images.unsplash.com/photo-1525385133512-2f3bdd039054?w=500",
        "time_minutes": 2,
        "difficulty": "Easy",
        "tag": "Healthy",
        "author": "admin",
        "ingredients": ["bread", "peanut butter", "banana", "honey"],
        "instructions": "1. Toast the bread until golden brown.\n2. Spread a thick layer of peanut butter.\n3. Slice the banana and place on top.\n4. Drizzle with honey."
    }
]

recipes.insert_many(sample_data)
print("Dorm recipes with ingredients added to the database!")