from db import Base, engine
from sqlalchemy import inspect
from models import Employee
# Проверяем наличие таблицы
inspector = inspect(engine)
if not inspector.has_table('employees'):
    # Создаем таблицу
    Employee.__table__.create(engine)
