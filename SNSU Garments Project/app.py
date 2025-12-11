from flask import Flask, request, session, render_template, redirect, url_for
import bcrypt 
import mysql.connector
import heapq

male = {}
female = {}

app = Flask(__name__)
app.secret_key = "mekierPogi"


# ---------------------- DATABASE CONNECTION ---------------------- #

database = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "snsu_garments_db"
)
cursor = database.cursor(dictionary = True)

# ----------------------  ROUTES GOES HERE ---------------------- #
@app.route("/")
def home():
    return render_template("auth.html")

# ---------------------- LOGIN ROUTE ---------------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        query = "SELECT id, username, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user:
            user_id, username, hashed = user

            if bcrypt.checkpw(password.encode("utf-8"), hashed): #type: ignore
                session["user_id"] = user_id
                session["username"] = username
                return redirect(url_for("user_home"))

        return "Invalid email or password"

    return render_template("auth.html")

# ---------------------- SIGNUP ROUTE ----------------------
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        school_id = request.form["school_id"]
        email = request.form["email"]
        password = request.form["password"]
        re_password = request.form["re_password"]

        if password != re_password:
            return "Passwords do not match!"

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        query = "INSERT INTO users (username, school_id ,email, password) VALUES (%s, %s, %s, %s)"

        try:
            cursor.execute(query, (username, school_id, email, hashed))
            database.commit()
            return redirect(url_for("home"))
        
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return redirect(url_for("home"))

# ---------------------- HOME/USER ROUTE ---------------------- #
@app.route("/home")
def user_home():
    if "user_id" not in session:
        return redirect(url_for("home"))
    return render_template("users.html")

# ---------------------- ADMIN ROUTE ---------------------- #
@app.route("/admin")
def admin_home():
    return render_template("admin.html")

# ---------------------- LOGOUT ROUTE ---------------------- #
@app.route("/logout")
def logout():
    return redirect(url_for("home"))

# ---------------------- STUDENT ENTRY ROUTE MALE ---------------------- #
@app.route("/male_entry", methods=["GET", "POST"])
def add_male_garments():
    if request.method == "POST":
        male_id = request.form["male-id"]
        male_polo_size = request.form["male-polo-size"]
        male_slacks_size = request.form["male-slacks-size"]
        male_shirt_size = request.form["male-shirt-size"]
        male_jp_size = request.form["male-jp-size"]

        # Check if student exists in users table (required)
        check_query = "SELECT school_id FROM users WHERE school_id = %s"
        cursor.execute(check_query, (male_id,))
        student_exists = cursor.fetchone()

        if not student_exists:
            # Student does NOT exist: reject the entry
            return f"Error: Student ID {male_id} not found in the system. Please register the student first."

        try:
            # Student exists: add to male_garments table
            query = "INSERT INTO male_garments (school_id, polo_size, slacks_size, shirt_size, jp_size) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (male_id, male_polo_size, male_slacks_size, male_shirt_size, male_jp_size))
            database.commit()
            return redirect(url_for("admin_home"))
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return redirect(url_for("admin_home"))

# ---------------------- STUDENT ENTRY ROUTE FEMALE ---------------------- #
@app.route("/female_entry", methods=["GET", "POST"])
def add_female_garments():
    if request.method == "POST":
        female_id = request.form["female-id"]
        female_blouse_size = request.form["female-blouse-size"]
        female_slacks_size = request.form["female-slacks-size"]
        female_skirt_size = request.form["female-skirt-size"]
        female_shirt_size = request.form["female-shirt-size"]
        female_jp_size = request.form["female-jp-size"]

        # Check if student exists in users table (required)
        check_query = "SELECT school_id FROM users WHERE school_id = %s"
        cursor.execute(check_query, (female_id,))
        student_exists = cursor.fetchone()

        if not student_exists:
            # Student does NOT exist: reject the entry
            return f"Error: Student ID {female_id} not found in the system. Please register the student first."

        try:
            # Student exists: add to female_garments table
            query = "INSERT INTO female_garments (school_id, blouse_size, slacks_size, skirt_size, shirt_size ,jp_size) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (female_id, female_blouse_size, female_slacks_size, female_skirt_size, female_shirt_size ,female_jp_size))
            database.commit()
            return redirect(url_for("admin_home"))
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return redirect(url_for("admin_home"))

if __name__ == '__main__':
    app.run(debug = True)