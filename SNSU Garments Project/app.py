from flask import Flask, request, session, render_template, redirect, url_for, jsonify
from collections import deque
import bcrypt 
import mysql.connector 
import heapq

student_map = {}

gigaNigga = [] 

claimable_boys_queue = deque()
claimable_girls_queue = deque()
waiting_boys_queue = deque()
waiting_girls_queue = deque()

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
            user_id = user["id"]
            username = user["username"]
            hashed = user["password"]

            if bcrypt.checkpw(password.encode("utf-8"), hashed):
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
    return redirect(url_for("admin_dashboard"))

# ---------------------- LOGOUT ROUTE ---------------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------------- STUDENT ENTRY ROUTE MALE ---------------------- #
@app.route("/male_entry", methods=["GET", "POST"])
def add_male_garments():
    if request.method == "POST":
        male_name = request.form["male-name"]
        male_id = request.form["male-id"]
        male_year = request.form["male-year"]
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
            query = "INSERT INTO male_garments (name, school_id, year_level ,polo_size, slacks_size, shirt_size, jp_size) VALUES (%s, %s, %s ,%s, %s, %s, %s)"
            cursor.execute(query, (male_name,male_id, male_year ,male_polo_size, male_slacks_size, male_shirt_size, male_jp_size))
            database.commit()
            return redirect(url_for("admin_home"))
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return redirect(url_for("admin_home"))

# ---------------------- STUDENT ENTRY ROUTE FEMALE ---------------------- #
@app.route("/female_entry", methods=["GET", "POST"])
def add_female_garments():
    if request.method == "POST":
        female_name = request.form["female-name"]
        female_id = request.form["female-id"]
        female_year = request.form["female-year"]
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
            query = "INSERT INTO female_garments (name, school_id, year_level, blouse_size, slacks_size, skirt_size, shirt_size ,jp_size) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (female_name,female_id, female_year ,female_blouse_size, female_slacks_size, female_skirt_size, female_shirt_size ,female_jp_size))
            database.commit()
            return redirect(url_for("admin_home"))
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return redirect(url_for("admin_home"))


def has_boys_stock(cursor, student):
    print("\n=== CHECKING BOYS STOCK ===")
    print("Student needs:", student)
    required = [
        ("Polo", "boys_stock", student["polo_size"]),
        ("Slacks", "boys_stock", student["slacks_size"]),
        ("Shirt", "pe_stock", student["shirt_size"]),
        ("Jogging Pants", "pe_stock", student["jp_size"]),
    ]

    for garment, table, size in required:
        if not size:
            print(f"Missing size for {garment}")
            return False
        
        cursor.execute(
            f"SELECT quantity FROM {table} WHERE garment_type=%s AND size=%s",
            (garment, size)
        )
        row = cursor.fetchone()
        print(f"Searching for: {garment} size {size} in {table} -> Found: {row}")
        
        if not row or row["quantity"] <= 0:
            print(f"FAILED: {garment} {size} not available or quantity <= 0")
            return False

    print("SUCCESS: All items available")
    return True


def has_girls_stock(cursor, student):
    print("\n=== CHECKING GIRLS STOCK ===")
    print("Student needs:", student)
    required = [
        ("Blouse", "girls_stock", student["blouse_size"]),
        ("Slacks", "girls_stock", student["slacks_size"]),
        ("Skirt", "girls_stock", student["skirt_size"]),
        ("Shirt", "pe_stock", student["shirt_size"]),
        ("Jogging Pants", "pe_stock", student["jp_size"]),
    ]

    for garment, table, size in required:
        if not size:
            print(f"Missing size for {garment}")
            return False

        cursor.execute(
            f"SELECT quantity FROM {table} WHERE garment_type=%s AND size=%s",
            (garment, size)
        )
        row = cursor.fetchone()
        print(f"Searching for: {garment} size {size} in {table} -> Found: {row}")
        
        if not row or row["quantity"] <= 0:
            print(f"FAILED: {garment} {size} not available or quantity <= 0")
            return False

    print("SUCCESS: All items available")
    return True


# ---------------------- LOAD STUDENT HASH TABLE ---------------------- #
def get_students_by_year(cursor):
    """Helper function to get students organized by year and claimed status"""
    cursor.execute("SELECT * FROM main_database ORDER BY year_level, school_id")
    all_students = cursor.fetchall()
    
    students_by_year = {
        "1": {"claimed": [], "unclaimed": []},
        "2": {"claimed": [], "unclaimed": []},
        "3": {"claimed": [], "unclaimed": []},
        "4": {"claimed": [], "unclaimed": []}
    }
    
    for student in all_students:
        year = student["year_level"]
        if year in students_by_year:
            if student["claimed"] == 1:
                students_by_year[year]["claimed"].append(student)
            else:
                students_by_year[year]["unclaimed"].append(student)
    
    return students_by_year


def load_students(cursor):
    student_map.clear()
    claimable_boys_queue.clear()
    claimable_girls_queue.clear()
    waiting_boys_queue.clear()
    waiting_girls_queue.clear()
    
    # ---- Load Male ---- #
    cursor.execute("SELECT * FROM male_garments")
    for row in cursor.fetchall():
        school_id = row['school_id']


        student_data = {
            "gender": "male",
            "year_level": row["year_level"],
            "name": row['name'],
            "polo_size": row['polo_size'],
            "slacks_size": row['slacks_size'],
            "shirt_size": row['shirt_size'],
            "jp_size": row['jp_size']
        }

        student_map[school_id] = student_data

        sizes_complete = all([
            student_data["polo_size"],
            student_data["slacks_size"],
            student_data["shirt_size"],
            student_data["jp_size"]
        ])

        is_claimable = sizes_complete and has_boys_stock(cursor, student_data)

                
        # Add to appropriate queue
        if is_claimable:
            claimable_boys_queue.append((school_id, student_data))
        else:
            waiting_boys_queue.append((school_id, student_data))


    # ---- Load Female ---- #
    cursor.execute("SELECT * FROM female_garments")
    for row in cursor.fetchall():
        school_id = row['school_id']

        student_data = {
        "gender": "female",
        "year_level": row["year_level"],
        "name": row['name'],
        "blouse_size": row['blouse_size'],
        "slacks_size": row['slacks_size'],
        "skirt_size": row['skirt_size'],
        "shirt_size": row['shirt_size'],
        "jp_size": row['jp_size']
    }
        
        student_map[school_id] = student_data
            
        sizes_complete = all([
            student_data["blouse_size"],
            student_data["slacks_size"],
            student_data["skirt_size"],
            student_data["shirt_size"],
            student_data["jp_size"]
        ])

        is_claimable = sizes_complete and has_girls_stock(cursor, student_data)

        
        # Add to appropriate queue
        if is_claimable:
            claimable_girls_queue.append((school_id, student_data))
        else:
            waiting_girls_queue.append((school_id, student_data))

        print("Loaded student:", school_id, student_data)


@app.route("/admin/dashboard")
def admin_dashboard():
    load_students(cursor)

      # Get lists from queues and sort by school_id
    claimable_boys = sorted(list(claimable_boys_queue), key=lambda x: x[0])
    claimable_girls = sorted(list(claimable_girls_queue), key=lambda x: x[0])
    waiting_boys = sorted(list(waiting_boys_queue), key=lambda x: x[0])
    waiting_girls = sorted(list(waiting_girls_queue), key=lambda x: x[0])

    # Load stock data
    cursor.execute("SELECT garment_type, size, quantity FROM boys_stock")
    boys_raw = cursor.fetchall()
    boys = {}
    for row in boys_raw:
        boys[(row['garment_type'], row['size'])] = row['quantity']

    cursor.execute("SELECT garment_type, size, quantity FROM girls_stock")
    girls_raw = cursor.fetchall()
    girls = {}
    for row in girls_raw:
        girls[(row['garment_type'], row['size'])] = row['quantity']

    cursor.execute("SELECT garment_type, size, quantity FROM pe_stock")
    pe_raw = cursor.fetchall()
    pe = {}
    for row in pe_raw:
        pe[(row['garment_type'], row['size'])] = row['quantity']

    print("Claimaible Boys Queue: ", claimable_boys_queue)
    print("Waiting Boys Queue: ", waiting_boys_queue)
    print("Claimable Girls Queue", claimable_girls_queue)
    print("Waiting Girls Queue: ", waiting_girls_queue)

    return render_template("admin.html", section="dashboard",
        claimable_boys=claimable_boys,
        claimable_girls=claimable_girls,
        waiting_boys=waiting_boys,
        waiting_girls=waiting_girls,
        boys=boys,
        girls=girls,
        pe=pe,
        students_by_year=get_students_by_year(cursor))


@app.route("/admin/stocks", methods=["GET", "POST"])
def add_stocks():
    if request.method == "POST":
        raw_value = request.form["garment-type"]   # e.g. "boys-polo" or "Jogging Pants"
        size = request.form["size"].upper()
        quantity = int(request.form["quantity"])

        # -----------------------------
        # SAFE SPLIT FOR BOYS/GIRLS
        # -----------------------------
        if "-" in raw_value:
            category, garment_type = raw_value.split("-")

            if category == "boys":
                table_name = "boys_stock"
            elif category == "girls":
                table_name = "girls_stock"
            else:
                return "Error: Unknown category"

        else:
            # -----------------------------
            # HANDLE PE ITEMS (NO DASH)
            # -----------------------------
            category = "pe"
            garment_type = raw_value.strip()    # Use full value e.g. "Jogging Pants"
            table_name = "pe_stock"

        try:
            query = f"""
                UPDATE {table_name}
                SET quantity = quantity + %s
                WHERE garment_type = %s AND size = %s
            """
            cursor.execute(query, (quantity, garment_type, size))
            database.commit()
            return redirect(url_for("add_stocks"))

        except mysql.connector.Error as err:
            return f"Error: {err}"

    # -----------------------------------
    # GET REQUEST → LOAD STOCK FROM MYSQL
    # -----------------------------------

    # Boys
    cursor.execute("SELECT garment_type, size, quantity FROM boys_stock")
    boys_raw = cursor.fetchall()

    boys = {}
    for row in boys_raw:
        garment = row['garment_type']
        size = row['size']
        qty = row['quantity']
        boys[(garment, size)] = qty

    # Girls
    cursor.execute("SELECT garment_type, size, quantity FROM girls_stock")
    girls_raw = cursor.fetchall()

    girls = {}
    for row in girls_raw:
        garment = row['garment_type']
        size = row['size']
        qty = row['quantity']
        girls[(garment, size)] = qty

    # PE
    cursor.execute("SELECT garment_type, size, quantity FROM pe_stock")
    pe_raw = cursor.fetchall()

    pe = {}
    for row in pe_raw:
        garment = row['garment_type']
        size = row['size']
        qty = row['quantity']
        pe[(garment, size)] = qty

    # ---------------------------------------
    # SEND STOCK DATA TO YOUR admin.html PAGE
    # ---------------------------------------
    return render_template(
        "admin.html",
        section="stocks",
        boys=boys,
        girls=girls,
        pe=pe,
        students_by_year=get_students_by_year(cursor)
    )

@app.route("/admin/database")
def admin_database():
    return render_template("admin.html", section="database", students_by_year=get_students_by_year(cursor))

@app.route("/admin/summary")
def admin_summary():
    return render_template("admin.html", section="summary", students_by_year=get_students_by_year(cursor))

# ---------------------- DEBUG ROUTE - CHECK STOCK ---------------------- #
@app.route("/debug/stock")
def debug_stock():
    cursor.execute("SELECT garment_type, size, quantity FROM boys_stock")
    boys_stock = cursor.fetchall()
    
    cursor.execute("SELECT garment_type, size, quantity FROM girls_stock")
    girls_stock = cursor.fetchall()
    
    cursor.execute("SELECT garment_type, size, quantity FROM pe_stock")
    pe_stock = cursor.fetchall()
    
    return jsonify({
        "boys_stock": boys_stock if boys_stock else [],
        "girls_stock": girls_stock if girls_stock else [],
        "pe_stock": pe_stock if pe_stock else []
    })


if __name__ == '__main__':
    app.run(debug = True)