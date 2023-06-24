import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from db import SessionLocal, Base
from models import Employee

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[SessionLocal] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
def test_create_employee(client):
    # Отправляем запрос на создание нового работника
    response = client.post(
        "/employees",
        json={
            "login": "test_user",
            "password": "test_password",
            "salary": 1000.0,
            "token": "Bearer test_token",
        }
    )

    # Проверяем статус код и сообщение в ответе
    assert response.status_code == 201
    assert response.json() == {"message": "Employee created successfully"}

def test_create_token(client):
    response = client.post("/token",
                           params={"login": "test_user", "password": "invalid_password"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Problems with authentication"}

def test_create_token_with_invalid_auth(client):
    response = client.post("/token",
                           params={"login": "test_user", "password": "invalid_password"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Problems with authentication"}

def test_delete_employee_by_login(client):
    # Создаем тестового работника в базе данных
    employee = Employee(login="test_user", password="test_password", salary=1000.0)
    db = TestingSessionLocal()

    # Отправляем запрос на удаление работника по логину
    response = client.delete(f"/employees/{employee.login}")

    # Проверяем статус код и убеждаемся, что работник удален из базы данных
    assert response.status_code == 204
    assert db.query(Employee).filter(str(Employee.login) == employee.login).first() is None


def test_delete_employee_by_login_not_found(client):
    # Отправляем запрос на удаление несуществующего работника по логину
    response = client.delete("/employees/nonexistent_user")

    # Проверяем статус код и сообщение об ошибке в ответе
    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}
