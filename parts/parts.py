import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем движок базы данных
SQLALCHEMY_DATABASE_URL = "postgresql://secUREusER:StrongEnoughPassword)@51.250.26.59:5432/query"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для объявления моделей SQLAlchemy
Base = declarative_base()

# Определяем модель parts для SQLAlchemy
class parts(Base):
    __tablename__ = "parts_shevich"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Подкласс BaseModel для создания модели данных Pydantic для parts
class partsModel(BaseModel):
    id: int
    name: str

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрут для создания записи
@app.post("/parts/", response_model=partsModel)
async def create_part(part: partsModel, db: Session = Depends(get_db)):
    db_part = parts(**part.dict())
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part

# Маршрут для чтения всех записей
@app.get("/parts/", response_model=List[partsModel])
async def read_parts(db: Session = Depends(get_db)):
    return db.query(parts).all()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))