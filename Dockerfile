# Используйте официальный образ Python в качестве базового образа
FROM python:3.11

# Установка переменной окружения для работы внутри контейнера
ENV PYTHONUNBUFFERED 1

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование файла зависимостей (poetry.lock и pyproject.toml) в контейнер
COPY poetry.lock pyproject.toml /app/

# Установка зависимостей с использованием Poetry
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Копирование всего содержимого проекта в контейнер
COPY . /app/
# Создаем базу данных
CMD ["python", "create_db.py"]
# Запуск сервера FastAPI при старте контейнера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
