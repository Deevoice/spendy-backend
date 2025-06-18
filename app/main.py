from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import engine, Base
from app.models import user, transaction, account, category
from app.api import (
    auth,
    accounts,
    categories,
    transactions,
    budgets,
    goals,
    blog,
)
from app.core.config import settings

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for personal finance tracking application",
    version=settings.VERSION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static avatars
os.makedirs("avatars", exist_ok=True)
app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(
    transactions.router, prefix="/api/transactions", tags=["transactions"]
)
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(blog.router, prefix="/api/blog", tags=["blog"])


@app.get("/")
async def root():
    return {"message": "Welcome to Spendy API"}
