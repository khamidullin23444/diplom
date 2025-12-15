from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import router
from app.database import Base, engine
import os

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

# Создаем приложение FastAPI
app = FastAPI(title="Robot Control System", version="1.0.0")

# Подключаем роутеры
app.include_router(router)

# Подключаем статические файлы
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "staticfiles")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

