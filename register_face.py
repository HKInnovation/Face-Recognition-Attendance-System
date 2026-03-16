import cv2
import os

STUDENT_NAME = input("Enter Student Name: ").strip()
SAVE_DIR = os.path.join("dataset", STUDENT_NAME)

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(0)
count = 0
MAX_IMAGES = 20

print("📸 Press SPACE to capture image, Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Register Face", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):
        img_path = os.path.join(SAVE_DIR, f"{count}.jpg")
        cv2.imwrite(img_path, frame)
        count += 1
        print(f"✅ Saved {img_path}")

    if key == ord('q') or count >= MAX_IMAGES:
        break

cap.release()
cv2.destroyAllWindows()

print("✅ Face capture completed")
print("➡️ Now run encode-faces.py")
