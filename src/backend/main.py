from fastapi import FastAPI

from src.backend.routers import auth, book_routers


app = FastAPI()
app.include_router(auth.router)
app.include_router(book_routers.book_router)