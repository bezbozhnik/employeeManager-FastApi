from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBasic
from passlib.context import CryptContext
from pydantic import BaseModel
import uuid
app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["scrypt"])

# Модель для данных о работнике
class Employee(BaseModel):
    login: str
    password: str
    salary: float
    promotion_date: datetime = datetime.now(timezone.utc) + timedelta(days=90) # Время до повышения
    token: str|None = None
    token_expiration: datetime|None = None

# Вместо базы данных используем простой словарь для хранения данных
employees_db = {}
tokens_db = {}
# Регистрация нового работника
@app.post("/employees")
async def create_employee(employee: Employee):
    # Хэшируем пароль перед сохранением в базу данных
    hashed_password = pwd_context.hash(employee.password)
    employee.password = hashed_password
    employees_db[employee.login] = employee
    return {"message": "Employee registered successfully"}
@app.post("/token")
async def create_token(login: str, password: str):
    if (employee := employees_db.get(login)) and pwd_context.verify(password, employee.password):
        if not employee.token or employee.token_expiration < datetime.now(timezone.utc):
            employee.token = generate_token()
            employee.token_expiration = datetime.now(timezone.utc) + timedelta(minutes=30) # Время действия 30 минут
            tokens_db[employee.token] = employee
            return {'token': employee.token}
        else:
            raise HTTPException(status_code=401, detail="There is an existing valid token")
    else:
        raise HTTPException(status_code=401, detail="Problems with authentication")

# Получение информации о зарплате и дате повышения через токен
@app.get("/info")
def get_info(token: str = None):
    # Проверяем наличие токена
    if token:
        if (employee := tokens_db.get(token)):
            if employee.token_expiration and employee.token_expiration > datetime.now(timezone.utc):
                return {"salary": employee.salary, "promotion_date": employee.promotion_date.strftime("%d/%m/%Y, %H:%M:%S")}
            else:
                raise HTTPException(status_code=401, detail="Token has expired")
        else:
            raise HTTPException(status_code=404, detail="Token not found")
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Генерация токена
def generate_token():
    return str(uuid.uuid4())
