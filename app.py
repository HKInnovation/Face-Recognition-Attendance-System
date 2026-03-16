from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
import os
import csv
import subprocess
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

DB_PATH = "attendance.db"
BACKUP_CSV = "deleted_backup.csv"
DATASET_PATH = "dataset"


# ---------------- DB CONNECTION ---------------- #
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CALCULATE WORKING HOURS ---------------- #
def calculate_hours(in_time, out_time):
    if not in_time or not out_time:
        return None
    try:
        t1 = datetime.strptime(in_time, "%H:%M:%S")
        t2 = datetime.strptime(out_time, "%H:%M:%S")
        diff = t2 - t1
        return str(diff)
    except:
        return None


# ---------------- HOME ---------------- #
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


# ---------------- DASHBOARD ---------------- #
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please login first.")
        return redirect(url_for('login'))

    name_filter = request.args.get('name', '')
    date_filter = request.args.get('date', '')

    query = "SELECT * FROM attendance WHERE 1=1"
    params = []

    if name_filter:
        query += " AND name LIKE ?"
        params.append(f"%{name_filter}%")

    if date_filter:
        query += " AND date = ?"
        params.append(date_filter)

    conn = get_db_connection()
    records = conn.execute(query, params).fetchall()
    conn.close()

    updated_records = []
    for r in records:
        updated_records.append({
            "id": r["id"],
            "name": r["name"],
            "date": r["date"],
            "time": r["time"],
            "out_time": r["out_time"],
            "hours": calculate_hours(r["time"], r["out_time"])
        })

    return render_template(
        'dashboard.html',
        records=updated_records,
        user=session['user']
    )


# ---------------- ADD STUDENT (ADMIN ONLY) ---------------- #
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session or session['user'] != 'admin':
        flash("Only admin can add students.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        name = request.form['name'].strip()
        image = request.files['image']

        if not name or not image:
            flash("Please provide name and image.")
            return redirect(url_for('add_student'))

        # Create main dataset folder if not exists
        if not os.path.exists(DATASET_PATH):
            os.makedirs(DATASET_PATH)

        # Create student folder
        student_folder = os.path.join(DATASET_PATH, name)

        if not os.path.exists(student_folder):
            os.makedirs(student_folder)

        # Save image inside the student folder
        filename = f"{name}.jpg"
        image_path = os.path.join(student_folder, filename)
        image.save(image_path)

        try:
            # Re-encode faces after adding new student
            subprocess.run(["python", "encode_faces.py"], check=True)
            flash("Student added and face encoded successfully ✅")

        except Exception as e:
            flash(f"Encoding failed: {str(e)}")

        return redirect(url_for('dashboard'))

    return render_template("add_student.html")

# ---------------- LOGIN ---------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        password = request.form['password']

        credentials = {
            "admin": "admin123",
            "teacher": "teacher123",
            "viewer": "viewer123"
        }

        if role in credentials and password == credentials[role]:
            session['user'] = role
            flash(f"Welcome, {role.capitalize()}!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))

    return render_template('login.html')


# ---------------- LOGOUT ---------------- #
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('home'))


# ---------------- DELETE (ADMIN) ---------------- #
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session or session['user'] != 'admin':
        flash("Only admin can delete records.")
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    record = conn.execute(
        "SELECT * FROM attendance WHERE id=?",
        (id,)
    ).fetchone()

    if record:
        file_exists = os.path.isfile(BACKUP_CSV)

        with open(BACKUP_CSV, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["ID", "Name", "Date", "IN Time", "OUT Time"])

            writer.writerow([
                record["id"],
                record["name"],
                record["date"],
                record["time"],
                record["out_time"]
            ])

        conn.execute("DELETE FROM attendance WHERE id=?", (id,))
        conn.commit()
        flash("Record deleted and backed up.")

    conn.close()
    return redirect(url_for('dashboard'))


# ---------------- UNDO DELETE ---------------- #
@app.route('/undo_delete')
def undo_delete():
    if 'user' not in session or session['user'] != 'admin':
        flash("Only admin can undo delete.")
        return redirect(url_for('dashboard'))

    if not os.path.exists(BACKUP_CSV):
        flash("No backup file found.")
        return redirect(url_for('dashboard'))

    with open(BACKUP_CSV, 'r') as f:
        rows = list(csv.reader(f))

    if len(rows) <= 1:
        flash("No deleted records to restore.")
        return redirect(url_for('dashboard'))

    last = rows[-1]

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO attendance (id, name, date, time, out_time)
        VALUES (?, ?, ?, ?, ?)
    """, (last[0], last[1], last[2], last[3], last[4]))
    conn.commit()
    conn.close()

    with open(BACKUP_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows[:-1])

    flash("Last deleted record restored successfully.")
    return redirect(url_for('dashboard'))


# ---------------- EXPORT CSV ---------------- #
@app.route('/export_csv')
def export_csv():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM attendance").fetchall()
    conn.close()

    filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Date", "IN Time", "OUT Time"])

        for row in data:
            writer.writerow([
                row["id"],
                row["name"],
                row["date"],
                row["time"],
                row["out_time"]
            ])

    return send_file(filename, as_attachment=True)


# ---------------- MARK ATTENDANCE ---------------- #
@app.route('/mark_attendance')
def mark_attendance():
    if 'user' not in session:
        flash("Please login first.")
        return redirect(url_for('login'))

    if session['user'] not in ['admin', 'teacher']:
        flash("Only Admin or Teacher can mark attendance.")
        return redirect(url_for('dashboard'))

    try:
        subprocess.run(["python", "recognize.py"], check=True)
        flash("📸 Attendance marking completed.")
    except Exception as e:
        flash(f"Error: {str(e)}")

    return redirect(url_for('dashboard'))


# ---------------- RUN APP ---------------- #
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)