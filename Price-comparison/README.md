# 🛒 Price Comparison App

A graduation project for comparing product prices across multiple stores. The system helps users browse products, compare prices, view discounts, manage favorites, and search for the best available deals through Arabic-friendly interfaces.

## ✨ Features

- Product price comparison across multiple stores
- Product browsing by categories
- Search by product name or description
- Discounts page showing products with reduced prices
- Favorites list for logged-in users
- User registration and login
- User profile and password update
- Arabic RTL interface
- Web application with Flask, Bootstrap, and Jinja2
- Cross-platform app with Python and Flet
- Shared MySQL database

## 🧰 Technologies Used

| Layer | Technologies |
|---|---|
| Web | Flask, HTML5, Bootstrap 5, Jinja2 |
| App UI | Python, Flet |
| Database | MySQL |
| Security | Werkzeug password hashing |
| Deployment / Demo | ngrok |

## 📁 Project Structure

```text
Price-comparison/
├── app/                         # Flet application
│   ├── main.py                  # App entry point and navigation
│   ├── db.py                    # MySQL connection helper
│   ├── session.py               # User session state
│   ├── components.py            # Shared UI components
│   └── pages/                   # Flet pages
│       ├── home_page.py
│       ├── categories_page.py
│       ├── product_page.py
│       ├── discounts_page.py
│       ├── favorites_page.py
│       ├── search_page.py
│       ├── login_page.py
│       ├── register_page.py
│       └── profile_page.py
│
├── web/                         # Flask web application
│   ├── app.py
│   ├── database.sql
│   └── templates/               # HTML + Bootstrap + Jinja2 templates
│
├── requirements.txt
├── .gitignore
└── .env.example
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Price-comparison.git
cd Price-comparison
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

Create the MySQL database by running the SQL file:

```bash
mysql -u root -p < web/database.sql
```

Or import `web/database.sql` using phpMyAdmin or MySQL Workbench.

### 5. Configure database credentials

Create a `.env` file based on `.env.example`, or edit the database credentials in `app/db.py` and `web/app.py` for local testing.

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_PASSWORD
DB_NAME=price_compare
FLASK_SECRET_KEY=change-this-secret-key
```

## ▶️ Running the Flet App

```bash
cd app
python main.py
```

The app runs in web browser mode on:

```text
http://localhost:8080
```

## ▶️ Running the Flask Web App

```bash
cd web
python app.py
```

The web app runs on:

```text
http://127.0.0.1:5000
```

## 🌍 Demo with ngrok

To expose the app publicly for remote demo:

```bash
ngrok http 8080
```

For the Flask web app:

```bash
ngrok http 5000
```

## 👤 My Contribution

Frontend Development:

- Designed and implemented user interfaces
- Built responsive pages using HTML5, Bootstrap 5, and Jinja2
- Supported Arabic RTL layout
- Improved page structure, navigation, and user experience
- Worked on pages such as Home, Categories, Product Details, Discounts, Favorites, Search, Login, Register, Profile, and Admin Dashboard

## 📌 Notes

- Do not upload `venv/`, `__pycache__/`, `.pyc` files, or `.env` files to GitHub.
- Keep database passwords and secret keys private.
- Use `.env.example` only as a template for configuration.

## 📄 License

This project is for educational purposes as a graduation project.
