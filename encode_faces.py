import face_recognition
import cv2
import os
import pickle

print("[INFO] Encoding faces...")

dataset_dir = "dataset"
known_encodings = []
known_names = []

# Loop through each student folder
for student_name in os.listdir(dataset_dir):
    person_folder = os.path.join(dataset_dir, student_name)
    if not os.path.isdir(person_folder):
        continue

    print(f"[INFO] Processing {student_name}...")
    for img_name in os.listdir(person_folder):
        img_path = os.path.join(person_folder, img_name)

        # Load and convert image
        image = cv2.imread(img_path)
        if image is None:
            print(f"[WARNING] Could not read {img_path}")
            continue

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect face(s)
        boxes = face_recognition.face_locations(rgb, model="hog")
        if len(boxes) == 0:
            print(f"[WARNING] No face found in {img_path}")
            continue

        # Encode the first face
        encodings = face_recognition.face_encodings(rgb, boxes)
        known_encodings.extend(encodings)
        known_names.extend([student_name] * len(encodings))

print(f"[INFO] Encoded {len(known_encodings)} faces total.")

# Save encodings
data = {"encodings": known_encodings, "names": known_names}
with open("labels.pickle", "wb") as f:
    pickle.dump(data, f)

print("[INFO] Encoding complete! Saved to labels.pickle")
