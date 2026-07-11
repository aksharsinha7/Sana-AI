import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, init_db, Student, ChatSession, Message
from ai_tutor import get_ai_response, GRADE_PROFILES, SUBJECTS

app = FastAPI(title="AI Teacher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# --- Schemas ---

class StudentCreate(BaseModel):
    name: str
    grade: int  # 0-12


class SessionCreate(BaseModel):
    student_id: int
    subject: str


class ChatMessage(BaseModel):
    session_id: int
    message: str


# --- Routes ---

@app.get("/grades")
def get_grades():
    return [{"value": k, "label": v["label"]} for k, v in GRADE_PROFILES.items()]


@app.get("/subjects")
def get_subjects():
    return SUBJECTS


@app.post("/students")
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    if not 0 <= data.grade <= 12:
        raise HTTPException(status_code=400, detail="Grade must be between 0 and 12")
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    student = Student(name=data.name.strip(), grade=data.grade)
    db.add(student)
    db.commit()
    db.refresh(student)
    return {"id": student.id, "name": student.name, "grade": student.grade, "grade_label": GRADE_PROFILES[student.grade]["label"]}


@app.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student.id, "name": student.name, "grade": student.grade, "grade_label": GRADE_PROFILES[student.grade]["label"]}


@app.get("/students/{student_id}/sessions")
def get_student_sessions(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    sessions = db.query(ChatSession).filter(ChatSession.student_id == student_id).all()
    return [
        {
            "id": s.id,
            "subject": s.subject,
            "started_at": s.started_at.isoformat(),
            "message_count": len(s.messages),
        }
        for s in sessions
    ]


@app.post("/sessions")
def create_session(data: SessionCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if data.subject not in SUBJECTS:
        raise HTTPException(status_code=400, detail=f"Subject must be one of: {SUBJECTS}")

    session = ChatSession(student_id=data.student_id, subject=data.subject)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id, "subject": session.subject, "student_id": session.student_id}


@app.get("/sessions/{session_id}/messages")
def get_messages(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp).all()
    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()} for m in messages]


@app.post("/chat")
def chat(data: ChatMessage, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message
    user_msg = Message(session_id=data.session_id, role="user", content=data.message)
    db.add(user_msg)
    db.commit()

    # Build conversation history from DB
    all_messages = (
        db.query(Message)
        .filter(Message.session_id == data.session_id)
        .order_by(Message.timestamp)
        .all()
    )
    conversation_history = [{"role": m.role, "content": m.content} for m in all_messages]

    # Get AI response + image
    result = get_ai_response(
        grade=session.student.grade,
        subject=session.subject,
        conversation_history=conversation_history,
    )

    # Save AI response
    ai_msg = Message(session_id=data.session_id, role="assistant", content=result["reply"])
    db.add(ai_msg)
    db.commit()

    return {"reply": result["reply"], "image": result["image"]}
