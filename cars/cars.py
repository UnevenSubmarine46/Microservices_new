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

# Определяем модель cars для SQLAlchemy
class cars(Base):
    __tablename__ = "cars_shevich"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Подкласс BaseModel для создания модели данных Pydantic для cars
class carsModel(BaseModel):
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
@app.post("/cars/", response_model=carsModel)
async def create_car(car: carsModel, db: Session = Depends(get_db)):
    db_car = cars(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# Маршрут для чтения всех записей
@app.get("/cars/", response_model=List[carsModel])
async def read_cars(db: Session = Depends(get_db)):
    return db.query(cars).all()

# Маршрут для чтения одной записи
@app.get("/cars/{car_id}", response_model=carsModel)
async def read_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(cars).filter(cars.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

# Маршрут для удаления записи
@app.delete("/cars/{car_id}")
async def delete_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(cars).filter(cars.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(car)
    db.commit()
    return {"message": "Car deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))