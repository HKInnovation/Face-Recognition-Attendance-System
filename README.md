# Face-Recognition-Attendance-System
An automated attendance system using face recognition technology to identify individuals and mark attendance. The system captures facial images through a camera, compares them with stored images in a database, and records attendance in real time, reducing manual work, errors, and saving time.

✨ Features

🎯 95–98% Accuracy — ResNet-based CNN (dlib) generates unique 128-dimensional face encodings

⚡ Real-Time Recognition — Processes live webcam feed frame by frame, marks attendance in under a second

🚫 Proxy Prevention — Physical face required; same student cannot be marked twice in one day

🖐️ Contactless — No touch, no cards, no physical interaction required

🔐 Role-Based Access — Admin, Teacher, and Viewer roles with separate permissions

📊 CSV Export — One-click download of attendance reports, filterable by name and date

💾 SQLite Database — Structured, tamper-resistant storage with automatic timestamps

🌐 Web Dashboard — Clean Flask-based UI accessible from any browser on the network

📦 No Retraining — Adding new students only requires capturing images and re-encoding

💻 Offline Capable — Works completely without internet; runs on any standard laptop + webcam

┌─────────────────────────────────────────────────────────────┐
│                        FRONT-END LAYER                      │
│   📷 Camera Module  →  User Interface  ←  Admin Panel      │
└──────────────────────────┬──────────────────────────────────┘
                           │ live feed
┌──────────────────────────▼──────────────────────────────────┐
│                      PROCESSING LAYER                       │
│                                                             │
│  Preprocessing → HOG Detection → ResNet CNN → Matching      │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │ fetch encodings / store records
┌──────────────────────────▼──────────────────────────────────┐
│                       DATABASE LAYER                        │
│         👤 User Database    📅 Attendance Database          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                        OUTPUT LAYER                         │
│         📋 Attendance Reports    ✅ Attendance Marking       │
└─────────────────────────────────────────────────────────────┘




<img width="634" height="301" alt="image" src="https://github.com/user-attachments/assets/b9f25e2d-2bd3-4961-b05f-c244d295f587" />

<img width="634" height="304" alt="image" src="https://github.com/user-attachments/assets/3a97c48e-1c22-4800-aac4-9c4d37ca8f71" />

<img width="634" height="316" alt="image" src="https://github.com/user-attachments/assets/4566dcfc-7c2f-4229-8e5c-432efb045957" />

<img width="634" height="326" alt="image" src="https://github.com/user-attachments/assets/2a4a61be-b859-4308-a09f-d888a9380554" />

<img width="634" height="335" alt="image" src="https://github.com/user-attachments/assets/7766ca7e-a2e0-4fe2-a282-989bc43989b8" />

