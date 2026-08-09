from flask import Flask, render_template, request, jsonify
import sqlite3
import uuid
import os


app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def init_db():

    conn = sqlite3.connect("civicsense.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT UNIQUE,
            location TEXT,
            category TEXT,
            description TEXT,
            priority TEXT,
            score INTEGER,
            department TEXT,
            insight TEXT,
            action TEXT
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    location = data.get("location", "")
    category = data.get("category", "")
    description = data.get("description", "")

    # Default values
    priority = "MEDIUM"
    score = 60

    # Basic intelligent priority detection
    text = description.lower()

    high_priority_words = [
        "danger",
        "accident",
        "emergency",
        "open manhole",
        "fire",
        "electric shock",
        "broken electric",
        "flood",
        "unsafe"
    ]

    for word in high_priority_words:
        if word in text:
            priority = "HIGH"
            score = 90
            break

    # Department and recommendation
    if category == "Garbage & Waste":

        department = "Municipal Waste Management"

        insight = (
            "The reported waste issue may create sanitation, "
            "environmental and public-health concerns."
        )

        action = (
            "Report the location to the municipal waste management "
            "authority and attach photographic evidence."
        )

    elif category == "Road & Potholes":

        department = "Public Works Department"

        insight = (
            "Road damage can affect traffic safety and may increase "
            "the risk of accidents."
        )

        action = (
            "Submit a road maintenance complaint with the exact "
            "location and photographic evidence."
        )

    elif category == "Street Lights":

        department = "Municipal Electrical Department"

        insight = (
            "A faulty street light can reduce visibility and "
            "create safety concerns, particularly at night."
        )

        action = (
            "Report the faulty street light with its exact location "
            "or nearby landmark."
        )

    elif category == "Water Supply":

        department = "Water Supply Department"

        insight = (
            "Water supply problems can affect residents and "
            "may require timely municipal intervention."
        )

        action = (
            "Report the issue with the affected location and "
            "duration of the problem."
        )

    elif category == "Drainage & Sewage":

        department = "Drainage & Sanitation Department"

        insight = (
            "Blocked or overflowing drainage can create sanitation "
            "and environmental risks."
        )

        action = (
            "Report the drainage issue immediately with location "
            "details and photographic evidence."
        )

    elif category == "Public Safety":

        department = "Local Civic / Public Safety Authority"

        insight = (
            "The reported issue may pose a direct risk to residents "
            "and should receive timely attention."
        )

        action = (
            "Report the issue to the appropriate civic authority "
            "and provide supporting evidence."
        )

    else:

        department = "Municipal Corporation"

        insight = (
            "CivicSense AI has identified a local civic concern "
            "that may require municipal attention."
        )

        action = (
            "Submit the issue with accurate location details "
            "and supporting evidence."
        )

    return jsonify({
        "success": True,
        "location": location,
        "category": category,
        "priority": priority,
        "score": score,
        "department": department,
        "insight": insight,
        "action": action
    })

@app.route("/submit-report", methods=["POST"])
def submit_report():

    location = request.form.get("location")
    category = request.form.get("category")
    description = request.form.get("description")

    priority = request.form.get("priority")
    score = request.form.get("score")
    department = request.form.get("department")
    insight = request.form.get("insight")
    action = request.form.get("action")

    photo = request.files.get("photo")

    photo_filename = None

    if photo and photo.filename:

        extension = os.path.splitext(photo.filename)[1]

        photo_filename = str(uuid.uuid4()) + extension

        photo.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                photo_filename
            )
        )

    report_id = "CS-" + str(uuid.uuid4())[:8].upper()

    conn = sqlite3.connect("civicsense.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports
        (report_id, location, category, description,
         priority, score, department, insight, action)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_id,
        location,
        category,
        description,
        priority,
        score,
        department,
        insight,
        action
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "report_id": report_id,
        "photo": photo_filename
    })
@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("civicsense.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Total reports
    cursor.execute("SELECT COUNT(*) FROM reports")
    total_reports = cursor.fetchone()[0]

    # High priority reports
    cursor.execute(
        "SELECT COUNT(*) FROM reports WHERE priority = 'HIGH'"
    )
    high_priority = cursor.fetchone()[0]

    # Medium priority reports
    cursor.execute(
        "SELECT COUNT(*) FROM reports WHERE priority = 'MEDIUM'"
    )
    medium_priority = cursor.fetchone()[0]

    # Category counts
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM reports
        GROUP BY category
        ORDER BY count DESC
    """)

    categories = cursor.fetchall()

    # Recent reports
    cursor.execute("""
        SELECT *
        FROM reports
        ORDER BY id DESC
        LIMIT 10
    """)

    reports = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_reports=total_reports,
        high_priority=high_priority,
        medium_priority=medium_priority,
        categories=categories,
        reports=reports
    )
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)