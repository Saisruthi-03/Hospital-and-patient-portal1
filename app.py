from flask import Flask, request, redirect, session, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "hospital_portal_secret_key"

DATABASE = "hospital.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# HTML template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Hospital and Patient Portal</title>
    <style>
        body {
            font-family: Arial;
            background: #eaf4f4;
            text-align: center;
            padding: 40px;
        }
        .container {
            background: white;
            padding: 30px;
            margin: auto;
            width: 350px;
            border-radius: 12px;
            box-shadow: 0 0 10px gray;
        }
        input {
            width: 90%;
            padding: 10px;
            margin: 10px;
        }
        button {
            background: #008080;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }
        a {
            color: #008080;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Hospital and Patient Portal</h2>
        {{ message|safe }}
        {{ content|safe }}
    </div>
</body>
</html>
"""


# Home page
@app.route("/")
def home():
    content = """
        <h3>Welcome to Hospital Portal</h3>
        <a href="/register">Patient Registration</a><br><br>
        <a href="/login">Patient Login</a>
    """
    return render_template_string(HTML, content=content, message="")


# Patient registration
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        try:
            hashed_password = generate_password_hash(password)

            conn.execute(
                "INSERT INTO patients (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            message = "Email already registered!"

    content = """
        <h3>Patient Registration</h3>
        <form method="POST">
            <input type="text" name="name"
                   placeholder="Full Name" required><br>

            <input type="email" name="email"
                   placeholder="Email" required><br>

            <input type="password" name="password"
                   placeholder="Password" required><br>

            <button type="submit">Register</button>
        </form>
        <a href="/">Back Home</a>
    """

    return render_template_string(
        HTML, content=content, message=message
    )


# Patient login
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        patient = conn.execute(
            "SELECT * FROM patients WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if patient and check_password_hash(
            patient["password"], password
        ):
            session["patient_id"] = patient["id"]
            session["patient_name"] = patient["name"]

            return redirect("/dashboard")

        message = "Invalid email or password!"

    content = """
        <h3>Patient Login</h3>
        <form method="POST">
            <input type="email" name="email"
                   placeholder="Email" required><br>

            <input type="password" name="password"
                   placeholder="Password" required><br>

            <button type="submit">Login</button>
        </form>
        <a href="/register">Create Account</a><br><br>
        <a href="/">Back Home</a>
    """

    return render_template_string(
        HTML, content=content, message=message
    )


# Patient dashboard
@app.route("/dashboard")
def dashboard():
    if "patient_id" not in session:
        return redirect("/login")

    name = session["patient_name"]

    content = f"""
        <h3>Welcome, {name}!</h3>
        <p>You are successfully logged in.</p>
        <h4>Patient Dashboard</h4>
        <p>Hospital and Patient Portal</p>
        <a href="/logout">Logout</a>
    """

    return render_template_string(
        HTML, content=content, message=""
    )


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# Run application
if __name__ == "__main__":
    init_db()
    app.run(debug=True)