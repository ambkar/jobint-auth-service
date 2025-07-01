FROM python:3.11-slim

WORKDIR /srv

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest>=8.4  pytest-asyncio>=1.0

COPY app ./app

CMD ["python", "-m", "app.main"]
