from typing import List, Optional, Dict
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session, JSON
from datetime import datetime

# Database Models
class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    title: str
    summary: str
    key_entities: Dict = Field(default={}, sa_type=JSON)  # Stores JSON object
    sections: List[str] = Field(default=[], sa_type=JSON) # Stores list of strings
    related_topics: List[str] = Field(default=[], sa_type=JSON) # Stores list of strings
    created_at: datetime = Field(default_factory=datetime.utcnow)

    questions: List["Question"] = Relationship(back_populates="quiz")

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    text: str
    answer: str
    difficulty: str
    explanation: str
    
    quiz: Optional[Quiz] = Relationship(back_populates="questions")
    options: List["Option"] = Relationship(back_populates="question")

class Option(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    text: str
    label: str # A, B, C, D

    question: Optional[Question] = Relationship(back_populates="options")

# Request/Response Schemas (Pydantic-like via SQLModel)
class QuestionRead(SQLModel):
    id: int
    text: str
    answer: str
    difficulty: str
    explanation: str
    options: List[str] 

class QuizRead(SQLModel):
    id: int
    url: str
    title: str
    summary: str
    key_entities: Dict
    sections: List[str]
    related_topics: List[str]
    created_at: datetime
    quiz: List[Dict] # Custom format matching User Request
