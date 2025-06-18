from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, transactions, categories
from app.core.config import settings

app = FastAPI(
    title="Spendy API", description="API для приложения Spendy", version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Разрешаем запросы с фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(
    transactions.router, prefix="/api/transactions", tags=["transactions"]
)
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])


@app.get("/")
async def root():
    return {"message": "Welcome to Spendy API"}
