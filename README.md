# Book API 📚

An asynchronous REST API for managing a collection of books, authors, and users. The project is built with a focus on clean architecture, high performance, and reliable test coverage.

## 🛠 Tech Stack

*   **Framework:** FastAPI
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy 2.0 (Async) + asyncpg
*   **Validation:** Pydantic
*   **Testing:** Pytest + pytest-asyncio
*   **Authentication:** JWT (JSON Web Tokens)

## ✨ Key Features

*   **Users:** Registration, profiles, secure password hashing, and JWT authorization. Role-based access control (regular users and administrators).
*   **Authors & Books (CRUD):** Full resource management via RESTful endpoints.
*   **Favorites:** Ability for users to add books to their favorites list (implemented via Many-to-Many relationships).
*   **Data Protection:** Validation at the Pydantic schema level and duplicate record prevention at the business logic level (HTTP 409 Conflict).
*   **Isolated Testing:** Automated creation and teardown of a dedicated test database (`book_api_test`) for each test, Dependency Overrides, and authorization mocking.

## 🚀 Running Locally

### 1. Clone and Setup Environment
```bash
git clone <your-repository-url>
cd book_api_fastapi

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # For Linux/MacOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
Create the main database in PostgeSQL:
```bash
CREATE DATABASE book_db
```

(Optional) Configure environment variables in a .env file (Database URL, JWT secret keys, etc.).

### 3. Run server
```bash
uvicorn src.backend.main:app --reload
```

Once running, the interactive API documentation (Swagger UI) will be available at: http://127.0.0.1:8000/docs

## 🧪 Testing
Testing requires a separate, isolated database. Create it in PostgreSQL before running the tests:
```bash
CREATE DATABASE book_api_test;
```
Ensure you have a pytest.ini file in the project root for proper module imports and async configuration:
```bash
[pytest]
pythonpath = .
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```
Run the entire test suite:
```bash
pytest -v tests/
```
## 📁 Project Structure
```plantuml
.
├── src/
│   └── backend/
│       ├── core/          # DB setup, security, dependencies
│       ├── models/        # SQLAlchemy ORM models
│       ├── schemas/       # Pydantic schemas for validation
│       ├── routers/       # FastAPI routers (endpoints)
│       ├── services/      # Business logic and DB interactions
│       └── main.py        # FastAPI entry point
├── tests/                 # Pytest test suite and conftest.py
├── pytest.ini             # Pytest configuration
└── requirements.txt       # Project dependencies
```