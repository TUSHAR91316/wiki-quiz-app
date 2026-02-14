from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from typing import List, Dict
from pydantic import BaseModel

from database import create_db_and_tables, get_session
from models import Quiz, Question, Option
import scraper
import ai_generator
import os

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mount moved to the end

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

class QuizRequest(BaseModel):
    urls: List[str]

@app.post("/api/generate", response_model=Dict)
def generate_quiz(request: QuizRequest, session: Session = Depends(get_session)):
    # 1. Scrape Wikipedia (Parallel)
    # request.urls is now a list
    article_data = scraper.scrape_wikipedia(request.urls)
    
    if not article_data:
        raise HTTPException(status_code=400, detail="Failed to scrape Wikipedia articles")

    # 2. Generate Quiz using Gemini
    # ... (rest of logic mostly similar, but we might store only primary URL or concat string in DB)
    quiz_content = ai_generator.generate_quiz_content(article_data['text'])
    
    if not quiz_content:
        raise HTTPException(status_code=500, detail="Failed to generate quiz")

    # 3. Save to DB
    # For multiple URLs, we'll store them as a comma-separated string in the 'url' field for now,
    # or just the first one if length constraint.
    # SQLModel 'url' field might be limited. Let's join them.
    stored_url = ", ".join(request.urls)
    
    quiz = Quiz(
        url=stored_url,
        title=article_data['title'][:200], # Truncate if too long
        summary=article_data['summary'],
        key_entities=quiz_content.get('key_entities', {}),
        sections=quiz_content.get('sections', []),
        related_topics=quiz_content.get('related_topics', [])
    )
    session.add(quiz)
    session.commit()
    session.refresh(quiz)

    # Save Questions & Options
    quiz_list = []
    # ai_generator.generate_quiz_content returns a DICT with 'quiz' key which is a list of dicts
    for q_data in quiz_content.get('quiz', []):
        question = Question(
            quiz_id=quiz.id,
            text=q_data['question'],
            answer=q_data['answer'],
            difficulty=q_data['difficulty'],
            explanation=q_data['explanation']
        )
        session.add(question)
        session.commit()
        session.refresh(question)
        
        for opt_text in q_data['options']:
            # Assign labels A, B, C, D locally if needed or just store text
            label = "ABCD"[q_data['options'].index(opt_text)] if len(q_data['options']) <=4 else "?"
            option = Option(question_id=question.id, text=opt_text, label=label) 
            session.add(option)
        
        quiz_list.append({
            "question": q_data['question'],
            "options": q_data['options'],
            "answer": q_data['answer'],
            "difficulty": q_data['difficulty'],
            "explanation": q_data['explanation']
        })
    
    session.commit()
    
    return build_quiz_response(quiz, session)

@app.get("/api/history", response_model=List[Dict])
def get_history(session: Session = Depends(get_session)):
    quizzes = session.exec(select(Quiz).order_by(Quiz.created_at.desc())).all()
    history = []
    for q in quizzes:
        history.append({
            "id": q.id,
            "title": q.title,
            "url": q.url,
            "summary": q.summary[:100] + "...", # Short summary for list
            "created_at": q.created_at.isoformat()
        })
    return history

@app.get("/api/quiz/{quiz_id}", response_model=Dict)
def get_quiz_details(quiz_id: int, session: Session = Depends(get_session)):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return build_quiz_response(quiz, session)

def build_quiz_response(quiz: Quiz, session: Session) -> Dict:
    # Helper to reconstruct the full JSON structure
    # Fetch questions
    questions = session.exec(select(Question).where(Question.quiz_id == quiz.id)).all()
    
    quiz_list = []
    for q in questions:
        options = session.exec(select(Option).where(Option.question_id == q.id)).all()
        # Sort options by label if needed, or just return text list
        # The prompt sample shows "options": ["A text", "B text"...]
        # and doesn't explicitly show labels in the string, but imply A-D.
        # Let's return just texts in list as requested.
        option_texts = [o.text for o in options]
        
        quiz_list.append({
            "question": q.text,
            "options": option_texts,
            "answer": q.answer,
            "difficulty": q.difficulty,
            "explanation": q.explanation
        })

    return {
        "id": quiz.id,
        "url": quiz.url,
        "title": quiz.title,
        "summary": quiz.summary,
        "key_entities": quiz.key_entities,
        "sections": quiz.sections,
        "quiz": quiz_list,
        "related_topics": quiz.related_topics
    }

# Mount frontend directory to serve static files
# Ensure frontend directory exists
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
