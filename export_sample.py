import json
from sqlmodel import Session, select, create_engine
from backend.models import Quiz, Question, Option  # Adjust import based on where script is run
from backend.database import engine # Adjust import

def export_latest_quiz():
    with Session(engine) as session:
        quiz = session.exec(select(Quiz).order_by(Quiz.created_at.desc())).first()
        if not quiz:
            print("No quiz found to export.")
            return

        # Reconstruct JSON
        questions = session.exec(select(Question).where(Question.quiz_id == quiz.id)).all()
        quiz_list = []
        for q in questions:
            options = session.exec(select(Option).where(Option.question_id == q.id)).all()
            quiz_list.append({
                "question": q.text,
                "options": [o.text for o in options],
                "answer": q.answer,
                "difficulty": q.difficulty,
                "explanation": q.explanation
            })

        data = {
            "id": quiz.id,
            "url": quiz.url,
            "title": quiz.title,
            "summary": quiz.summary,
            "key_entities": quiz.key_entities,
            "sections": quiz.sections,
            "quiz": quiz_list,
            "related_topics": quiz.related_topics
        }

        with open("sample_data/sample_quiz.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Exported sample_data/sample_quiz.json")

if __name__ == "__main__":
    export_latest_quiz()
