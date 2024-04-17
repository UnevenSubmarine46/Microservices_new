import os
import uvicorn


from keycloak.keycloak_openid import KeycloakOpenID

#from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, HTTPException, Depends, Form, Header
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
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


#Keycloak
# Данные для подключения к Keycloak
KEYCLOAK_URL = "http://localhost:8180/"
KEYCLOAK_CLIENT_ID = "shevich"
KEYCLOAK_REALM = "cars_service_realm"
KEYCLOAK_CLIENT_SECRET = "Dntb8bgmeAprD7UizHzxqd7XOwM7GhIb"

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                 client_id=KEYCLOAK_CLIENT_ID,
                                 realm_name=KEYCLOAK_REALM,
                                 client_secret_key=KEYCLOAK_CLIENT_SECRET)

user_token = ""

#Instrumentator().instrument(app).expose(app)

@app.post("/get-token")
async def get_token(username: str = Form(...), password: str = Form(...)):
    try:
        # Получение токена
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        return token
    except Exception as e:
        print(e)  # Логирование для диагностики
        raise HTTPException(status_code=400, detail="Не удалось получить токен")


def check_user_roles(token):
    try:
        token_info = keycloak_openid.introspect(token)
        if "testRole" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")

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
async def create_car(car: carsModel, db: Session = Depends(get_db),token: str = Header(...)):
    if check_user_roles(token):
        db_car = cars(**car.dict())
        db.add(db_car)
        db.commit()
        db.refresh(db_car)
        return db_car
    else:
        return "Wrong JWT Token"
# Маршрут для чтения всех записей
@app.get("/cars/", response_model=List[carsModel])
async def read_cars(db: Session = Depends(get_db),token: str = Header(...)):
    if check_user_roles(token):
        return db.query(cars).all()
    else:
        return "Wrong JWT Token"

# Маршрут для чтения одной записи
@app.get("/cars/{car_id}", response_model=carsModel)
async def read_car(car_id: int, db: Session = Depends(get_db)):

    car = db.query(cars).filter(cars.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


# Маршрут для удаления записи
@app.delete("/cars/{car_id}")
async def delete_car(car_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    if check_user_roles(token):
        car = db.query(cars).filter(cars.id == car_id).first()
        if car is None:
            raise HTTPException(status_code=404, detail="Car not found")
        db.delete(car)
        db.commit()
        return {"message": "Car deleted successfully"}
    else:
        return "Wrong JWT Token"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))