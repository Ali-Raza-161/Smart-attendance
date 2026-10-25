"""Smart Attendance API. Educational demo only — not a medical or
security-critical system, and face data requires written consent.
Uploaded photos are never stored; only embeddings are stored, and only
when a model is available and consent is recorded."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.services.db import init_db
from api.routers import auth, people, sessions, reports

app = FastAPI(title="Smart Attendance System",
              description="Educational face-recognition attendance demo. "
              "Consent, deletion, manual fallback and audit logging are built in. "
              "No real face photos or model weights are included.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True, "service": "smart-attendance",
            "note": "Educational demo. Face recognition requires a downloaded model; without it, enrollment/recognition return 503, never a fake match."}

for _r in (auth.router, people.router, sessions.router, reports.router):
    app.include_router(_r, prefix="/api")
