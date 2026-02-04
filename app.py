from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "greenroots_secret"

# ---------- DATABASE CONNECTION ----------
def get_db():
    return sqlite3.connect("database.db")

# ---------- CREATE TABLES ----------
with get_db() as con:
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            address TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS plantation(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            plant TEXT,
            location TEXT,
            growth INTEGER
        )
    """)

# ---------- SPLASH ----------
@app.route("/")
def splash():
    return render_template("splash.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cur.fetchone()

        if user:
            session["user"] = user[1]
            return redirect("/home")

    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = (
            request.form["name"],
            request.form["email"],
            request.form["password"],
            request.form["address"]
        )

        con = get_db()
        con.cursor().execute(
            "INSERT INTO users(name,email,password,address) VALUES(?,?,?,?)",
            data
        )
        con.commit()
        return redirect("/login")

    return render_template("register.html")

# ---------- HOME ----------
@app.route("/home")
def home():
    con = get_db()
    plants = con.cursor().execute(
        "SELECT * FROM plantation"
    ).fetchall()
    return render_template("home.html", plants=plants)

# ---------- ADD PLANT ----------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = (
            session["user"],
            request.form["plant"],
            request.form["location"],
            25
        )

        con = get_db()
        con.cursor().execute(
            "INSERT INTO plantation(user,plant,location,growth) VALUES(?,?,?,?)",
            data
        )
        con.commit()
        return redirect("/home")

    return render_template("add_plantation.html")

# ---------- VIEW PLANT ----------
@app.route("/view")
def view():
    con = get_db()
    plants = con.cursor().execute(
        "SELECT * FROM plantation"
    ).fetchall()
    return render_template("view_plantation.html", plants=plants)

# ---------- UPDATE GROWTH ----------
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    con = get_db()

    if request.method == "POST":
        growth = request.form["growth"]
        con.cursor().execute(
            "UPDATE plantation SET growth=? WHERE id=?",
            (growth, id)
        )
        con.commit()
        return redirect("/view")

    plant = con.cursor().execute(
        "SELECT * FROM plantation WHERE id=?",
        (id,)
    ).fetchone()

    return render_template("update_growth.html", plant=plant)

# ---------- PROFILE ----------
@app.route("/profile")
def profile():
    con = get_db()
    user = con.cursor().execute(
        "SELECT * FROM users WHERE name=?",
        (session["user"],)
    ).fetchone()
    return render_template("profile.html", user=user)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
