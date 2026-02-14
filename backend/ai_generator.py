import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Define Pydantic models for structured output
class Question(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 options (A-D)")
    answer: str = Field(description="The correct answer from the options")
    difficulty: str = Field(description="Difficulty level: easy, medium, or hard")
    explanation: str = Field(description="Short explanation of the answer")

class QuizOutput(BaseModel):
    key_entities: Dict[str, List[str]] = Field(description="Extracted key entities: people, organizations, locations")
    sections: List[str] = Field(description="Main sections or topics covered in the quiz")
    quiz: List[Question] = Field(description="List of 5-10 quiz questions")
    related_topics: List[str] = Field(description="List of 3-5 related Wikipedia topics for further reading")

def generate_quiz_content(text: str) -> dict:
    """
    Generates a quiz from the provided text using Gemini via LangChain.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key, temperature=0.7)

    # Setup Parser
    parser = PydanticOutputParser(pydantic_object=QuizOutput)

    # Define Prompt
    prompt_template = """
    You are an expert educator and quiz creator. Based on the following article text, create a comprehensive quiz.
    
    Article content:
    {text}
    
    Requirements:
    1. Generate 5-10 multiple-choice questions.
    2. Each question must have 4 options, one correct answer, a difficulty level, and an explanation.
    3. Extract key entities (people, organizations, locations).
    4. Identify main sections found in the text.
    5. Suggest related Wikipedia topics.
    6. Ensure the output is valid JSON matching the specified format.
    
    {format_instructions}
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # Create Chain
    chain = prompt | llm | parser

    # Truncate text if too long (Gemini Flash has large context, but let's be safe for rate limits/speed)
    # 20k chars is usually safe for detailed scraping
    safe_text = text[:30000] 

    try:
        result = chain.invoke({"text": safe_text})
        return result.dict()
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return None

if __name__ == "__main__":
    # Test the generator (Requires .env with GEMINI_API_KEY)
    # Mock text for testing
    mock_text = "Alan Mathison Turing was a British mathematician, computer scientist, logician, cryptanalyst, philosopher, and theoretical biologist."
    try:
        quiz = generate_quiz_content(mock_text)
        print(json.dumps(quiz, indent=2))
    except Exception as e:
        print(f"Test failed: {e}")
