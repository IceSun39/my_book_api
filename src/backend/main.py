import os
from fastapi import FastAPI
from src.backend.routers.book_routes import book_router
from src.backend.routers.author_routes import author_router
from src.backend.routers.user_routes import user_router
from src.backend.routers.auth import auth_router
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(debug=os.getenv("DEBUG", "False").lower() == "true")
app.include_router(book_router)
app.include_router(author_router)
app.include_router(user_router)
app.include_router(auth_router)