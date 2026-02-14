# Wiki Quiz Generator 🧠

A full-stack application that generates interactive quizzes from Wikipedia articles using AI. Built with **FastAPI**, **PostgreSQL**, and **Vanilla JS**.

## 🚀 Features

-   **AI-Powered Quiz Generation**: Extracts content from Wikipedia and uses **Gemini AI** to accept relevant questions.
-   **Multi-Link Support**: supports parsing multiple Wikipedia URLs at once to create a combined quiz.
-   **Interactive UI**: Clean, card-based layout with **Dark Mode** support.
-   **History Tracking**: Stores past quizzes in a database for easy retrieval.
-   **Scoring System**: Real-time score tracking as you take the quiz.
-   **Responsive Design**: Works on desktop and mobile.

## 🛠️ Tech Stack

-   **Backend**: Python (FastAPI), SQLModel (SQLAlchemy), BeautifulSoup4 (Scraping), LangChain (AI).
-   **Database**: PostgreSQL (Recommended) or MySQL (Compatible). code defaults to SQLite for easy local testing but is production-ready for Postgres.
-   **Frontend**: HTML5, CSS3, Vanilla JavaScript (No Node.js frameworks).
-   **AI Model**: Google Gemini Pro / Flash (via free tier API).

## 📂 Project Structure

```
wiki-quiz-app/
├── backend/
│   ├── main.py           # FastAPI Entry Point
│   ├── models.py         # Database Models (SQLModel)
│   ├── database.py       # DB Connection Logic
│   ├── scraper.py        # Wikipedia Scraper (BeautifulSoup)
│   ├── ai_generator.py   # LangChain AI Logic
│   ├── requirements.txt  # Python Dependencies
│   └── .env              # Environment Variables
├── frontend/
│   ├── index.html        # Main UI
│   ├── style.css         # Styling (Dark Mode included)
│   └── script.js         # Frontend Logic & API calls
├── sample_data/          # Example JSON outputs for testing
├── prompts.md            # documented LangChain prompts
└── README.md             # This file
```

## ⚙️ Setup Instructions

### 1. Backend Setup

1.  **Clone the repository** and navigate to `backend/`.
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment**:
    -   Rename `.env.example` to `.env`.
    -   Add your **GEMINI_API_KEY**.
    -   (Optional) Update `DATABASE_URL` to point to your PostgreSQL instance.
        ```
        DATABASE_URL=postgresql://user:password@localhost/wiki_quiz_db
        ```
5.  **Run the Server**:
    ```bash
    uvicorn main:app --reload
    ```
    The API will start at `http://127.0.0.1:8000`.

### 2. Frontend Setup

1.  Simply open `frontend/index.html` in your browser.
2.  Or, since the backend serves static files, go to `http://127.0.0.1:8000/`.

## 🧪 Testing

1.  **Generate Quiz**:
    -   Go to **Tab 1**.
    -   Paste a Wikipedia URL (e.g., `https://en.wikipedia.org/wiki/Alan_Turing`).
    -   Click **Generate Quiz**.
2.  **History**:
    -   Go to **Tab 2** to see your past quizzes.
    -   Click **Details** to view them again.

## 📊 Sample Data

Check the `sample_data/` folder for example JSON responses returned by the API.

## 📝 API Endpoints

-   `POST /api/generate`: Generates a quiz from a list of URLs.
-   `GET /api/history`: Returns a list of past quizzes.
-   `GET /api/quiz/{id}`: Returns full details of a specific quiz.

## 🤖 Prompts

The specific prompts used to instruct the AI are documented in `prompts.md`.

---
*Built for DeepKlarity Technologies Assignment.*
