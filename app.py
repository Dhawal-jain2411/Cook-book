from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import certifi

load_dotenv()
app = Flask(__name__)
app.secret_key = "dr2_super_secret_key"

client = MongoClient(
    os.getenv("MONGO_URI"),
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True
)
db = client["cookbook_db"]
recipes_collection = db["recipes"]
users_collection = db["users"]

def attach_avg_ratings(recipes):
    for r in recipes:
        comments = r.get("comments", [])
        if comments:
            r["avg_rating"] = round(sum(c.get("rating", 0) for c in comments) / len(comments), 1)
        else:
            r["avg_rating"] = 0
    return recipes

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password")
        if users_collection.find_one({"username": username}):
            return render_template("register.html", error="Username already taken!")

        hashed_password = generate_password_hash(password)
        is_admin = True if username == "admin" else False

        users_collection.insert_one({
            "username": username,
            "password": hashed_password,
            "favorites": [],
            "status": "active",
            "bio": "",
            "is_admin": is_admin
        })
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password")
        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            if user.get("status") == "disabled":
                return render_template("login.html", error="Your account has been disabled by an Admin.")

            session["username"] = user["username"]
            session["is_admin"] = user.get("is_admin", False)
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    if "username" not in session: return redirect(url_for("login"))
    search_query = request.args.get("search")
    category_filter = request.args.get("category")

    db_query = {}
    if search_query:
        db_query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"ingredients": {"$regex": search_query, "$options": "i"}}
        ]
    if category_filter:
        db_query["tag"] = category_filter

    filtered_recipes = attach_avg_ratings(list(recipes_collection.find(db_query)))
    all_categories = sorted([c for c in recipes_collection.distinct("tag") if c])

    user = users_collection.find_one({"username": session["username"]})
    user_favs = user.get("favorites", []) if user else []

    return render_template(
        "index.html",
        recipes=filtered_recipes,
        categories=all_categories,
        user_favs=user_favs
    )

@app.route("/recipe/<recipe_id>")
def recipe_detail(recipe_id):
    if "username" not in session: return redirect(url_for("login"))
    recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})

    comments = recipe.get("comments", [])
    avg_rating = round(sum(c.get("rating", 0) for c in comments) / len(comments), 1) if comments else 0

    user = users_collection.find_one({"username": session["username"]})
    is_fav = recipe_id in (user.get("favorites", []) if user else [])

    return render_template("recipe_detail.html", recipe=recipe, avg_rating=avg_rating, is_fav=is_fav)

@app.route("/recipe/<recipe_id>/comment", methods=["POST"])
def add_comment(recipe_id):
    if "username" not in session: return redirect(url_for("login"))

    new_comment = {
        "username": session["username"],
        "text": request.form.get("comment_text"),
        "rating": int(request.form.get("rating"))
    }

    recipes_collection.update_one(
        {"_id": ObjectId(recipe_id)},
        {"$push": {"comments": new_comment}}
    )
    return redirect(url_for("recipe_detail", recipe_id=recipe_id))

@app.route("/add-recipe", methods=["GET", "POST"])
def add_recipe():
    if "username" not in session: return redirect(url_for("login"))

    if request.method == "POST":
        raw_ingredients = request.form.get("ingredients")
        ingredients_list = [i.strip() for i in raw_ingredients.split(",") if i.strip()]

        selected_tag = request.form.get("tag")
        if selected_tag == "__other__":
            final_tag = request.form.get("custom_tag", "").strip()
        else:
            final_tag = selected_tag.strip()

        new_recipe = {
            "title": request.form.get("title"),
            "image_url": request.form.get("image_url"),
            "time_minutes": int(request.form.get("time_minutes")),
            "difficulty": request.form.get("difficulty"),
            "tag": final_tag,
            "ingredients": ingredients_list,
            "instructions": request.form.get("instructions"),
            "author": session["username"],
            "comments": []
        }
        recipes_collection.insert_one(new_recipe)
        all_categories = sorted([c for c in recipes_collection.distinct("tag") if c])
        return render_template("add_recipe.html", success=True, categories=all_categories)

    all_categories = sorted([c for c in recipes_collection.distinct("tag") if c])
    return render_template("add_recipe.html", success=False, categories=all_categories)

@app.route("/my-recipes")
def my_recipes():
    if "username" not in session: return redirect(url_for("login"))
    user_recipes = attach_avg_ratings(list(recipes_collection.find({"author": session["username"]})))
    return render_template("my_recipes.html", recipes=user_recipes)

@app.route("/edit-recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if "username" not in session: return redirect(url_for("login"))
    recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})

    if not recipe or (recipe["author"] != session["username"] and not session.get("is_admin")):
        return redirect(url_for("my_recipes"))

    if request.method == "POST":
        raw_ingredients = request.form.get("ingredients")
        ingredients_list = [i.strip() for i in raw_ingredients.split(",") if i.strip()]

        recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$set": {
                "title": request.form.get("title"),
                "image_url": request.form.get("image_url"),
                "time_minutes": int(request.form.get("time_minutes")),
                "difficulty": request.form.get("difficulty"),
                "tag": request.form.get("tag").strip(),
                "ingredients": ingredients_list,
                "instructions": request.form.get("instructions")
            }}
        )
        return redirect(url_for("my_recipes"))

    return render_template("edit_recipe.html", recipe=recipe)

@app.route("/delete-recipe/<recipe_id>", methods=["POST"])
def delete_recipe(recipe_id):
    if "username" not in session: return redirect(url_for("login"))
    recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    if recipe and (recipe["author"] == session["username"] or session.get("is_admin")):
        recipes_collection.delete_one({"_id": ObjectId(recipe_id)})
        users_collection.update_many({}, {"$pull": {"favorites": recipe_id}})
    return redirect(request.referrer or url_for("home"))

@app.route("/favorite/<recipe_id>", methods=["POST"])
def toggle_favorite(recipe_id):
    if "username" not in session: return redirect(url_for("login"))
    user = users_collection.find_one({"username": session["username"]})
    favs = user.get("favorites", []) if user else []

    if recipe_id in favs:
        users_collection.update_one(
            {"username": session["username"]},
            {"$pull": {"favorites": recipe_id}}
        )
    else:
        users_collection.update_one(
            {"username": session["username"]},
            {"$addToSet": {"favorites": recipe_id}}
        )
    return redirect(request.referrer or url_for("home"))

@app.route("/favorites")
def favorites():
    if "username" not in session: return redirect(url_for("login"))
    user = users_collection.find_one({"username": session["username"]})
    fav_string_ids = user.get("favorites", []) if user else []
    obj_ids = [ObjectId(fid) for fid in fav_string_ids if ObjectId.is_valid(fid)]
    fav_recipes = attach_avg_ratings(list(recipes_collection.find({"_id": {"$in": obj_ids}})))
    return render_template("favorites.html", recipes=fav_recipes)

@app.route("/profile")
def profile():
    if "username" not in session: return redirect(url_for("login"))
    user = users_collection.find_one({"username": session["username"]})
    my_upload_count = recipes_collection.count_documents({"author": session["username"]})
    my_fav_count = len(user.get("favorites", []))

    return render_template("profile.html", user=user, uploads=my_upload_count, favs=my_fav_count)

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session: return redirect(url_for("login"))
    user = users_collection.find_one({"username": session["username"]})

    if request.method == "POST":
        new_bio = request.form.get("bio")
        new_password = request.form.get("password")

        update_fields = {"bio": new_bio}
        if new_password:
            update_fields["password"] = generate_password_hash(new_password)

        users_collection.update_one(
            {"username": session["username"]},
            {"$set": update_fields}
        )
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=user)

@app.route("/admin")
def admin_panel():
    if not session.get("is_admin"): return redirect("/")
    all_users = list(users_collection.find())
    all_recipes = list(recipes_collection.find())
    return render_template("admin.html", users=all_users, recipes=all_recipes)

@app.route("/admin/toggle_user/<username>", methods=["POST"])
def toggle_user(username):
    if not session.get("is_admin"): return redirect("/")
    user = users_collection.find_one({"username": username})
    new_status = "disabled" if user.get("status", "active") == "active" else "active"
    users_collection.update_one({"username": username}, {"$set": {"status": new_status}})
    return redirect("/admin")

@app.route("/admin/toggle_admin/<username>", methods=["POST"])
def toggle_admin(username):
    if not session.get("is_admin"): return redirect("/")
    if username == "admin":
        return redirect("/admin")

    user = users_collection.find_one({"username": username})
    new_role = not user.get("is_admin", False)
    users_collection.update_one({"username": username}, {"$set": {"is_admin": new_role}})
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)