import uuid
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.security import HTTPBasic
from passlib.context import CryptContext
from pydantic import BaseModel

import models
from db import SessionLocal

app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["scrypt"])
db = SessionLocal()


class Employee(BaseModel):
    login: str
    password: str
    salary: float
    promotion_date: datetime = datetime.now(timezone.utc) + timedelta(days=90)  # Время до повышения
    token: str | None = None
    token_expiration: datetime | None = None

    class Config:
        orm_mode = True


# Регистрация нового работника
@app.post("/employees", status_code=status.HTTP_201_CREATED)
async def create_employee(employee: Employee):
    new_employee = models.Employee(
        login=employee.login,
        password=pwd_context.hash(employee.password),
        salary=employee.salary,
        promotion_date=employee.promotion_date,
        token=employee.token,
        token_expiration=employee.token_expiration,
    )
    db.rollback()
    db.add(new_employee)
    db.commit()
    return {'message': 'Employee created successfully'}

# Удаление работника
@app.delete("/employees/{login}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee_by_login(login: str):
    employee = db.query(models.Employee).filter(models.Employee.login == login).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()

# Создание токена через логин и пароль
@app.post("/token", status_code=status.HTTP_201_CREATED)
async def create_token(login: str, password: str):
    employee = db.query(models.Employee).filter(models.Employee.login == login).first()
    if employee and pwd_context.verify(password, employee.password):
        if not employee.token or employee.token_expiration.astimezone(timezone.utc) < datetime.now(timezone.utc):
            employee.token = generate_token()
            employee.token_expiration = datetime.now(timezone.utc) + timedelta(minutes=30)
            db.commit()
            return {'token': employee.token}
        else:
            raise HTTPException(status_code=401, detail="There is an existing valid token")
    else:
        db.close()
        raise HTTPException(status_code=401, detail="Problems with authentication")


# Получение информации о зарплате и дате повышения через токен
@app.get("/info")
async def get_info(token: str = None):
    if token:
        employee = db.query(models.Employee).filter(models.Employee.token == token).first()
        if employee:
            if employee.token_expiration and employee.token_expiration.astimezone(timezone.utc) > datetime.now(
                    timezone.utc):
                return {
                    "salary": employee.salary,
                    "promotion_date": employee.promotion_date.strftime("%d/%m/%Y, %H:%M:%S")
                }
            else:
                raise HTTPException(status_code=401, detail="Token has expired")
        else:
            raise HTTPException(status_code=404, detail="Token not found")
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Генерация токена
def generate_token():
    return str(uuid.uuid4())
