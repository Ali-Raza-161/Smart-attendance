# Smart Attendance System using Face Recognition
Prepared by Ali Raza | Version 1.0

> **Privacy and consent — read first:** This is an educational system.
> Take written consent before enrolling anyone (parent consent for minors).
> Store embeddings only where possible, not raw photos. Allow any person
> to request full deletion of their face data. A manual attendance option
> is always available for people who do not consent. Face data is
> sensitive personal data — this demo includes no real face photos,
> no real people's embeddings, and no model weights.

## 1. Project Overview
Smart Attendance marks student or employee attendance automatically
using face recognition. A camera captures faces in a classroom or
office, the system detects each face, converts it into a numerical
face embedding using a deep learning model, compares it with the
registered people in the database, and marks the matched person as
present. Teachers and administrators use a web dashboard to manage
classes, view attendance, and download reports.

## 2. Problem Statement
Traditional attendance by calling names or signing a sheet wastes
class time, allows proxy attendance (one student marking for another)
and creates paperwork that is hard to analyze. Card or fingerprint
systems need special hardware and physical contact. A face-recognition
system saves time, reduces proxy attendance and keeps accurate
digital records.

## 3. Objectives
- Register people with a few face images through a simple enrollment process.
- Detect and recognize multiple faces from a live camera or an uploaded class photo.
- Mark attendance automatically with date, time and class.
- Reduce fake attendance using liveness (anti-spoofing) checks.
- Provide a web dashboard with reports, filters and Excel export.
- Protect privacy and store only what is necessary.
- Deploy the system and measure its accuracy.

## 4. Scope
In scope: enrollment, face detection, face recognition, attendance
marking, liveness check, dashboard, reports, user roles, privacy controls.
Out of scope (future work): hardware door-access control, mask-wearing
recognition, large-scale multi-campus deployment, mobile app.

## 5. Features
### 5.1 Admin features
- Login with secure authentication (JWT + bcrypt).
- Add classes, courses and people (students or employees).
- Enroll faces by uploading photos or capturing from the webcam
  (5 to 10 images per person from different angles).
- Delete a person and all of their face data on request
  (`DELETE /api/people/:id` removes the person, all embeddings and
  their attendance records, and audit-logs the deletion).

### 5.2 Teacher features
- Start an attendance session for a class.
- Capture attendance from a live webcam or upload a classroom photo.
- Review and correct results before saving (mark absent as present, or the reverse).
- View and export attendance reports.

### 5.3 System features
- Multi-face detection in one frame.
- Duplicate prevention: one attendance record per person per session.
- Unknown face handling: unrecognized faces are flagged for review
  (below-threshold matches return no identity, never a guessed name).
- Liveness detection to reduce spoofing with printed photos or phone screens.
- Attendance percentage and low-attendance alerts.

## 6. Languages and Technologies Used
### 6.1 Programming and markup languages
| Language | Where it is used |
|---|---|
| Python | Face detection, recognition, API and database logic |
| TypeScript | React web dashboard |
| JavaScript | Build configuration and small scripts |
| HTML5 | Page structure and webcam access through React JSX |
| CSS3 / Tailwind CSS | Styling and responsive design (this build uses clean CSS; see Demo notes) |
| SQL | PostgreSQL queries (SQLite locally, same SQLAlchemy models) |
| JSON | API requests and responses |
| Markdown | README and documentation |

### 6.2 Libraries and frameworks
| Area | Technology |
|---|---|
| Computer vision | OpenCV, NumPy, Pillow |
| Face detection | RetinaFace, MTCNN or YuNet (OpenCV); Haar cascade fallback in `ai/detector.py` |
| Face recognition | InsightFace (ArcFace) or FaceNet (facenet-pytorch); DeepFace as an alternative wrapper |
| Deep learning runtime | PyTorch or ONNX Runtime |
| Matching | Cosine similarity or Euclidean distance on 512-dimension embeddings; optional FAISS for fast search |
| Liveness detection | Eye-blink and head-movement check, or a lightweight anti-spoofing CNN |
| Backend API | FastAPI, Uvicorn, Pydantic |
| Database | PostgreSQL with SQLAlchemy (embeddings stored as arrays or with pgvector); SQLite fallback locally |
| Authentication | JWT, bcrypt |
| Reports | Pandas, openpyxl or ExcelJS (Excel export) |
| Frontend | React, Vite, Tailwind CSS, react-webcam, Recharts |
| Testing | Pytest, Vitest |
| Tools | Git, GitHub, Docker, Postman, VS Code, Google Colab |
| Deployment | Render or Railway (API), Vercel (frontend), Neon or Supabase (database) |

## 7. System Architecture
Two main flows.

**Enrollment flow:** Admin uploads or captures face images, then the
face is detected and cropped, then the model creates an embedding for
each image, then the embeddings are stored in the database linked to
the person. Raw photos are never stored.

**Attendance flow:** Teacher starts a session and captures a frame,
then all faces are detected, then a liveness check runs, then each
face is converted to an embedding, then it is compared with the stored
embeddings, then if the similarity is above the threshold the person
is marked present, otherwise the face is marked unknown, then the
teacher reviews and saves the result.

Components: React client, FastAPI server, face recognition module
(`ai/`), PostgreSQL database, and a report generator.

## 8. Face Recognition Methodology
1. **Face detection:** locate every face in the image and return bounding boxes and landmarks (eyes, nose, mouth).
2. **Alignment and preprocessing:** crop and align the face using landmarks, resize to the model's input size (for example 112 by 112), and normalize pixel values.
3. **Embedding extraction:** a deep network (ArcFace or FaceNet) converts the face into a 512-number vector that represents its identity.
4. **Matching:** compare the new embedding with the stored embeddings using cosine similarity. The best match is accepted only if the score is above a threshold (for example 0.5, tuned on test data).
5. **Decision:** matched faces are marked present; low-score faces are labeled Unknown.
6. **Liveness check:** before accepting a match, check for natural signs of a live person (eye blinks or small head movement) to reduce photo and screen spoofing.

## 9. Evaluation
| Metric | Meaning |
|---|---|
| Accuracy | Percentage of correctly recognized faces |
| False Acceptance Rate (FAR) | Wrong person accepted (must be very low) |
| False Rejection Rate (FRR) | Correct person rejected |
| Precision and recall | Quality of present and unknown decisions |
| Processing time | Seconds per frame and per class photo |

Testing should include different lighting, camera distances, head
angles, glasses, beards and group photos of 20 to 40 people. The
threshold is chosen to keep FAR very low while keeping FRR acceptable.
`ai/evaluate.py` implements these metrics; in this build they are
verified only on synthetic fixtures (see Demo notes) — they are NOT
real face-accuracy numbers.

## 10. Database Design
- **users:** id, name, email, password_hash, role (admin or teacher), created_at
- **people:** id, name, roll_or_employee_no, class_id, status, consent, created_at
- **face_embeddings:** id, person_id, embedding (vector of 512 numbers, stored as JSON locally; pgvector in Postgres), created_at
- **classes:** id, name, teacher_id, created_at
- **sessions:** id, class_id, date, start_time, created_by, created_at
- **attendance:** id, session_id, person_id, status (present, absent, late), confidence, marked_at, marked_by (system or teacher)
- **audit_logs:** id, action, user_id, target, created_at (added for privacy auditing)

Relationships: a class has many people and many sessions; a session
has many attendance records; a person has many face embeddings.

## 11. API Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/login | Login and receive a JWT |
| GET / POST | /api/classes | List or create classes |
| GET / POST | /api/people | List or add people |
| POST | /api/people/:id/enroll | Upload face images for enrollment |
| DELETE | /api/people/:id | Delete a person and all face data |
| POST | /api/sessions | Start an attendance session |
| POST | /api/sessions/:id/recognize | Send a frame or photo and receive recognized faces |
| GET | /api/sessions/:id/attendance | Attendance table for a session (for review) |
| PATCH | /api/attendance/:id | Teacher corrects a record |
| GET | /api/reports/attendance | Attendance report with filters |
| GET | /api/reports/export | Download Excel report |
| GET | /health | API health check |

## 12. Folder Structure
```
smart-attendance/
  ai/
    detector.py       (face detection)
    embedder.py       (embedding extraction)
    matcher.py        (similarity and threshold logic)
    liveness.py       (anti-spoofing check)
    evaluate.py       (accuracy, FAR, FRR tests)
  api/
    main.py
    routers/          (auth.py, people.py, sessions.py, reports.py)
    models/           (SQLAlchemy models)
    schemas/          (Pydantic models)
    services/         (db.py, auth.py, audit.py)
  web/
    src/
      components/     (WebcamCapture, FaceBoxOverlay, AttendanceTable)
      pages/          (Login, Dashboard, People, Enroll, TakeAttendance, Reports)
      services/       (api.ts)
  scripts_create_admin.py
  tests/
  README.md
```

## 13. User Interface Pages
- **Login:** admin and teacher sign in.
- **Dashboard:** today's attendance, class percentage, low-attendance list.
- **People and Enroll:** add people and capture face images with guidance (look straight, left, right).
- **Take Attendance:** live camera view with face boxes and names, review table before saving.
- **Reports:** filters by class, date range and person, with Excel export.

## 14. Privacy, Ethics and Security
Face data is sensitive personal data, so the project follows these rules:
- Take written consent before enrolling anyone (and parent consent for minors). Enrollment is blocked (`400`) if `consent` is not recorded.
- Store only face embeddings, not raw photos, wherever possible.
- Encrypt the database and use HTTPS in deployment; set a strong `SECRET_KEY` (never use the dev default in production).
- Allow a person to request deletion of all their face data.
- Restrict access with roles and JWT; keep an audit log of changes.
- Explain clearly where the camera is used and why (shown on the Take Attendance page).
- Test for bias across skin tones, genders and ages, and report the results honestly.
- Keep a manual attendance option for people who do not consent (sessions start with everyone absent; the teacher corrects the table).

## 15. Testing Plan
- Model testing: accuracy, FAR and FRR on a test set of enrolled and unknown people.
- Condition testing: low light, side angles, glasses, caps, group photos.
- Spoofing test: printed photo and phone screen attempts.
- API testing: valid, invalid and oversized images.
- UI testing: camera permissions, review and save flow.

Tests actually run in this build (see Demo notes): matcher on
synthetic vectors, liveness logic, and API flow (login, class/person/
session, correction, consent gate, invalid/oversized images, deletion,
Excel export).

## 16. Setup Guide
### AI and API
1. Install Python 3.10 or later and create a virtual environment.
2. Install packages: `pip install -r requirements.txt` (fastapi, uvicorn, sqlalchemy, pyjwt, bcrypt, openpyxl, pytest, plus optional opencv-python, insightface or facenet-pytorch, onnxruntime, psycopg2-binary for a real model).
3. Create a `.env` file with `DATABASE_URL` and `SECRET_KEY`.
4. Create the first user: `python scripts_create_admin.py "Admin Name" admin@example.com your-password admin`
5. Run: `uvicorn api.main:app --reload` (from the project root; API on http://localhost:8000, docs at /docs).
6. To enable real recognition, install OpenCV + an embedding backend and download its model weights, then wire it in `ai/detector.py` / `ai/embedder.py`. Until then, enrollment/recognition return 503, never a fake match.

### Web app
1. Go to the `web` folder and run `npm install`.
2. Set `VITE_API_URL` in a `.env` file (default http://localhost:8000/api).
3. Run `npm run dev` (Vite on http://localhost:5173).

## 17. Deployment
- Frontend on Vercel.
- API on Render or Railway using Docker (the recognition model runs on CPU for small classes).
- PostgreSQL on Neon or Supabase.
- For real classrooms, a local computer or Raspberry Pi with a webcam can run the recognition module.

## 18. Development Timeline
| Week | Task |
|---|---|
| 1 | Requirements, literature review, environment setup |
| 2 | Face detection and embedding extraction experiments |
| 3 | Matching, threshold tuning and accuracy tests |
| 4 | Liveness check |
| 5 | FastAPI backend, database and enrollment |
| 6 | React dashboard and camera attendance page |
| 7 | Reports, testing and bug fixing |
| 8 | Deployment, documentation and presentation |

## 19. Limitations
- Accuracy drops in poor lighting, extreme angles or low-quality cameras.
- Look-alike people and twins can cause errors.
- Simple liveness checks cannot stop all advanced spoofing attacks.
- Face recognition raises privacy concerns and needs clear consent and policy.

## 20. Future Improvements
- Stronger anti-spoofing with depth or infrared cameras.
- Mobile app for teachers.
- Automatic notifications to parents about absence.
- Integration with the school fee management system and student records.
- Edge deployment on Raspberry Pi or Jetson Nano.
- Support for masked faces.

## 21. Conclusion
The Smart Attendance System shows a complete computer vision pipeline,
from face detection and deep learning embeddings to matching, liveness
checking, a web dashboard and deployment. It solves a real problem for
schools and offices while addressing privacy and ethics, which makes
it a strong project for university submission, a portfolio and AI/ML
interviews.

## Demo notes (read before showing this to anyone)
- **No real faces, no model weights:** no face photos, no real
  embeddings, and no `.onnx` / `.pth` / `.keras` weights are included.
  Tests use synthetic 512-dimension vectors (random numbers, not
  faces) and synthetic blank images (expect no face / 503, not a match).
- **Model backends are optional and lazy:** OpenCV, InsightFace and
  FaceNet are NOT installed in this build's venv. `ai/detector.py`
  raises `DetectorUnavailable` and `ai/embedder.py` raises
  `ModelNotAvailable` in that case; the API returns 503. Verified:
  a valid blank PNG to `/recognize` returned 503 with that message.
- **Tests run:** Pytest 17/17 passed (matcher, liveness, API flow).
  Frontend `npm run build` succeeded (99 modules, JS 225.63 kB).
- **Styling:** clean CSS, not Tailwind — Tailwind was skipped for a
  reliable build; component/page structure is unchanged. Webcam uses
  the native browser camera API, with file-upload fallback (no
  react-webcam dependency); Recharts is not wired in this build.
- **Database:** locally SQLite (same SQLAlchemy models); live
  Postgres was NOT tested. Use Neon/Supabase Postgres for production.
- **NOT verified:** real face-recognition accuracy, FAR/FRR on real
  faces, liveness against printed photos/screens, live deployment,
  and browser camera click-through (camera permission cannot be
  tested by a generic agent). Do not claim those numbers.
- **No default account is shipped.** Create one with
  `scripts_create_admin.py`; never use the dev `SECRET_KEY` default
  in production.
