# Development Challenges & Solutions

This document logs the technical issues encountered during the development of the Wiki Quiz App and how they were resolved.

## 1. Database Connection (`OperationalError`)
- **Issue**: The application failed to start because the PostgreSQL database `wiki_quiz_db` did not exist.
- **Error**: `FATAL: database "wiki_quiz_db" does not exist`
- **Solution**: Updated `backend/database.py` to check for the database's existence on startup and automatically create it if missing, using a temporary connection to the default `postgres` database.

## 2. API 405 Method Not Allowed
- **Issue**: `POST /api/generate` returned `405 Method Not Allowed`.
- **Cause**: The Frontend Static Files were mounted at the root URL (`/`) *before* the API routes were defined. FastAPI matches routes in order, so it was trying to handle API requests as static file lookups.
- **Solution**: Moved `app.mount("/", ...)` to the very end of `backend/main.py` so that specific API routes are matched first.

## 3. Wikipedia Scraper 403 Forbidden
- **Issue**: The `requests.get()` call to Wikipedia failed with status `403`.
- **Cause**: Wikipedia blocks requests that do not create a `User-Agent` header (identifying scripts).
- **Solution**: Added a standard browser `User-Agent` header to the scraper in `backend/scraper.py`.

## 4. Gemini API Model Availability (404 / 429 Errors)
- **Issue**: Finding a working free-tier model for the provided API key was difficult.
    - `gemini-1.5-flash`: Returned `400/404` initially (likely version mismatch).
    - `gemini-pro`: Returned `404 Not Found` (deprecated or restricted).
    - `gemini-2.0-flash` & `gemini-2.0-flash-lite`: Returned `429 Resource Exhausted` with a quota limit of 0 (Preview models not available on this tier).
- **Solution**: Switched to **`gemini-flash-latest`**, which correctly points to the stable, free-tier supported version of Gemini Flash.

## 5. Syntax Error (Missing Return)
- **Issue**: `SyntaxError: unmatched '}'` preventing startup.
- **Cause**: Accidental deletion of a `return` statement while refactoring `main.py`.
- **Solution**: Restored the missing code block in `build_quiz_response`.
