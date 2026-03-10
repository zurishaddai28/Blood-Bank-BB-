from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "bloodbanksecret"

# DATABASE
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS donors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        blood_group TEXT,
        phone TEXT,
        city TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# HOME
@app.route("/")
def index():
    return render_template("index.html")


# ADD DONOR
@app.route("/add", methods=["GET","POST"])
def add_donor():

    if request.method == "POST":

        name = request.form["name"]
        blood_group = request.form["blood_group"]
        phone = request.form["phone"]
        city = request.form["city"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO donors(name,blood_group,phone,city) VALUES (?,?,?,?)",
        (name,blood_group,phone,city)
        )

        conn.commit()
        conn.close()

        return redirect("/donors")

    return render_template("add_donor.html")


# VIEW DONORS
@app.route("/donors")
def donors():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM donors")
    data = cur.fetchall()

    conn.close()

    return render_template("donors.html", donors=data)


# SEARCH
@app.route("/search", methods=["POST"])
def search():

    group = request.form["blood_group"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM donors WHERE blood_group=?", (group,))
    data = cur.fetchall()

    conn.close()

    return render_template("donors.html", donors=data)


# ADMIN LOGIN
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/donors")

    return render_template("admin_login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


# EDIT DONOR (ADMIN ONLY)
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_donor(id):

    if "admin" not in session:
        return "Access Denied"

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        blood_group = request.form["blood_group"]
        phone = request.form["phone"]
        city = request.form["city"]

        cur.execute("""
        UPDATE donors
        SET name=?, blood_group=?, phone=?, city=?
        WHERE id=?
        """,(name,blood_group,phone,city,id))

        conn.commit()
        conn.close()

        return redirect("/donors")

    cur.execute("SELECT * FROM donors WHERE id=?", (id,))
    donor = cur.fetchone()

    conn.close()

    return render_template("edit_donor.html", donor=donor)


if __name__ == "__main__":
    app.run(debug=True)