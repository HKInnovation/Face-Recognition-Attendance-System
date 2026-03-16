import cv2
import face_recognition
import pickle
import sqlite3
import os
from datetime import datetime, timedelta

# ---------------- CONFIG ---------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "attendance.db")
ENCODING_FILE = os.path.join(BASE_DIR, "labels.pickle")

MIN_GAP_MINUTES = 2

# ---------------- LOAD ENCODINGS ---------------- #
print("Loading encodings...")

with open(ENCODING_FILE, "rb") as f:
    data = pickle.load(f)

# ---------------- DB CONNECTION ---------------- #
def get_db():
    return sqlite3.connect(DB_PATH)

# ---------------- ATTENDANCE LOGIC ---------------- #
def mark_attendance(name):

    conn = get_db()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    cur.execute("""
        SELECT id, time, out_time FROM attendance
        WHERE name=? AND date=?
    """, (name, today))

    row = cur.fetchone()

    # -------- FIRST ENTRY (IN TIME) -------- #
    if row is None:

        cur.execute("""
            INSERT INTO attendance (name, date, time, out_time)
            VALUES (?, ?, ?, NULL)
        """, (name, today, now_time))

        print(f"[IN] {name} at {now_time}")

    else:

        record_id, in_time, out_time = row

        # -------- OUT TIME -------- #
        if out_time is None:

            in_datetime = datetime.strptime(
                f"{today} {in_time}", "%Y-%m-%d %H:%M:%S"
            )

            now_datetime = datetime.now()
            gap = now_datetime - in_datetime

            if gap >= timedelta(minutes=MIN_GAP_MINUTES):

                cur.execute("""
                    UPDATE attendance
                    SET out_time=?
                    WHERE id=?
                """, (now_time, record_id))

                print(f"[OUT] {name} at {now_time}")

            else:
                print(f"[BLOCKED] {name} OUT attempt (gap < 2 mins)")

        else:
            print(f"[SKIPPED] {name} already marked IN & OUT")

    conn.commit()
    conn.close()


# ---------------- FACE RECOGNITION ---------------- #

video = cv2.VideoCapture(0)

print("📷 Camera started. Press 'q' to quit.")

last_seen = {}

while True:

    ret, frame = video.read()

    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)

    for encoding, box in zip(encodings, boxes):

        matches = face_recognition.compare_faces(
            data["encodings"], encoding, tolerance=0.5
        )

        name = "Unknown"

        if True in matches:

            matched_idxs = [i for i, v in enumerate(matches) if v]

            counts = {}

            for i in matched_idxs:
                matched_name = data["names"][i]
                counts[matched_name] = counts.get(matched_name, 0) + 1

            name = max(counts, key=counts.get)

            now = datetime.now()

            # Prevent multiple triggers within 5 seconds
            if name not in last_seen or (now - last_seen[name]).seconds > 5:

                mark_attendance(name)
                last_seen[name] = now

        top, right, bottom, left = box

        cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)

        cv2.putText(
            frame,
            name,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

    cv2.imshow("Face Recognition Attendance", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


video.release()
cv2.destroyAllWindows()

print("✅ Camera closed. Attendance process completed.")