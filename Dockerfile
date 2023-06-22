FROM python:3.11

COPY . /app

RUN pip install poetry

WORKDIR /app

RUN poetry install --no-dev

CMD ["python", "app.py"]