FROM python:3.11-slim

WORKDIR /srv

# 1. зависимости (prod + тесты)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest>=8.4 pytest-asyncio>=1.0

# 2. конфигурация Alembic + исходный код
COPY alembic.ini .
COPY app ./app

# 3. миграции ➜ старт Sanic
CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]
