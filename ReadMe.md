# 🍳 CookBook :DR2

A full-stack recipe-sharing web application built with **Python (Flask)** and **MongoDB Atlas**. Designed for students and home cooks to discover, share, rate, and save quick recipes—complete with reverse-ingredient search, dynamic categories, and role-based access control.

---

## ✨ Key Features

- **User Authentication & RBAC:** Secure registration and login with password hashing (`Werkzeug`) and an Admin Panel to manage user accounts (enable/disable) and promote or demote admins.
- **Reverse-Ingredient Search:** Search recipes by dish name or by ingredients you already have on hand.
- **Dynamic Categories:** Filter recipes by category on the home feed, and add new categories on the fly using the **"Other (Add New Category)"** dropdown option.
- **Star Ratings & Reviews:** Post 1–5 star ratings and reviews on any recipe; average ratings display directly on the Home, Favorites, and Recipe Detail pages.
- **One-Click Favorites Toggle:** Easily save or remove favorite recipes from the home feed, recipe detail page, or favorites tab.
- **Full CRUD Operations:** Create, view, edit, and delete your own recipes anytime.
- **Clean UI with Background Watermark:** Responsive card layout paired with a subtle global background watermark.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, Flask, PyMongo, Werkzeug Security |
| **Database** | MongoDB Atlas (Cloud NoSQL) |
| **Frontend** | HTML5, CSS3, Jinja2 Templates |
| **Environment** | `python-dotenv`, `certifi` |

---

## 🚀 Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Dhawal-jain2411/Cook-book.git](https://github.com/Dhawal-jain2411/Cook-book.git)
   cd Cook-book
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   *(On macOS/Linux, run `source venv/bin/activate`)*

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory and add your MongoDB Atlas connection string:
   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/cookbook_db?retryWrites=true&w=majority
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your browser.

---

## 🛡️ Security Note

- Sensitive credentials are stored in `.env` and excluded from version control via `.gitignore`.
- Passwords are never stored in plain text; all user credentials are salted and hashed using `werkzeug.security`.
