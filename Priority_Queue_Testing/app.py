from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import heapq
import time

app = Flask(__name__)

# ---------------------- DATABASE CONNECTION ---------------------- #
database = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="garments_example_db"
)
cursor = database.cursor(dictionary=True)

# ---------------------- PYTHON HASH TABLE (for quick lookup) ---------------------- #
student_hash = {}      # key = school_id, value = record from DB

# ---------------------- PRIORITY QUEUES ---------------------- #
male_pq = []        # [(priority, timestamp, school_id)]
female_pq = []

# Priority rule: lower number = higher priority
PRIORITY_COMPLETE_STOCK = 1
PRIORITY_INCOMPLETE_STOCK = 2


# ---------------------- HELPER: LOAD STUDENTS INTO HASH TABLE ---------------------- #
def load_hash_table():
    student_hash.clear()

    cursor.execute("SELECT * FROM male_garments")
    for row in cursor.fetchall():
        student_hash[row["school_id"]] = row

    cursor.execute("SELECT * FROM female_garments")
    for row in cursor.fetchall():
        student_hash[row["school_id"]] = row


# ---------------------- HELPER: CHECK STOCK ---------------------- #
def has_complete_stock(gender, blouse=None, slacks=None, skirt=None, shirt=None, jp=None):
    """ Returns True if all sizes are available in stock. """
    query = "SELECT * FROM stock WHERE gender = %s"
    cursor.execute(query, (gender,))
    stock = cursor.fetchone()

    if gender == "female":
        return (
            int(stock["blouse_" + blouse]) > 0 and
            int(stock["slacks_" + slacks]) > 0 and
            int(stock["skirt_" + skirt]) > 0 and
            int(stock["shirt_" + shirt]) > 0 and
            int(stock["jp_" + jp]) > 0 
        ) 

    if gender == "male":
        return (
            int(stock["polo_" + blouse]) > 0 and
            int(stock["slacks_" + slacks]) > 0 and
            int(stock["shirt_" + shirt]) > 0 and
            int(stock["jp_" + jp]) > 0
        )

    return False


# ---------------------- ROUTE: HOME ---------------------- #
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------- FEMALE ENTRY ---------------------- #
@app.route("/female_entry", methods=["POST"])
def female_entry():
    school_id = request.form["school_id"]
    blouse = request.form["blouse"]
    slacks = request.form["slacks"]
    skirt = request.form["skirt"]
    shirt = request.form["shirt"]
    jp = request.form["jp"]

    # Save to DB
    query = """
        INSERT INTO female_garments (school_id, blouse_size, slacks_size, skirt_size, shirt_size, jp_size)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (school_id, blouse, slacks, skirt, shirt, jp))
    database.commit()

    load_hash_table()

    # Determine priority
    if has_complete_stock("female", blouse, slacks, skirt, shirt, jp):
        priority = PRIORITY_COMPLETE_STOCK
    else:
        priority = PRIORITY_INCOMPLETE_STOCK

    heapq.heappush(female_pq, (priority, time.time(), school_id))

    return render_template("success.html", message="Female entry added!")


# ---------------------- MALE ENTRY ---------------------- #
@app.route("/male_entry", methods=["POST"])
def male_entry():
    school_id = request.form["school_id"]
    polo = request.form["polo"]
    slacks = request.form["slacks"]
    shirt = request.form["shirt"]
    jp = request.form["jp"]

    query = """
        INSERT INTO male_garments (school_id, polo_size, slacks_size, shirt_size, jp_size)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (school_id, polo, slacks, shirt, jp))
    database.commit()

    load_hash_table()

    # Determine priority
    if has_complete_stock("male", polo, slacks, shirt, jp):
        priority = PRIORITY_COMPLETE_STOCK
    else:
        priority = PRIORITY_INCOMPLETE_STOCK

    heapq.heappush(male_pq, (priority, time.time(), school_id))

    return render_template("success.html", message="Male entry added!")


# ---------------------- SHOW WAITING LIST ---------------------- #
@app.route("/waiting")
def waiting_list():
    return render_template(
        "waiting_list.html",
        male_queue=male_pq,
        female_queue=female_pq,
        students=student_hash
    )


# ---------------------- SHOW STOCK ---------------------- #
@app.route("/stock")
def stock():
    cursor.execute("SELECT * FROM stock")
    data = cursor.fetchall()
    return render_template("stock.html", stock=data)


# ---------------------- START APP ---------------------- #
if __name__ == "__main__":
    load_hash_table()
    app.run(debug=True)
