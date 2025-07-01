FROM python:3.11-slim

WORKDIR /srv
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./               # app.py, auth.py, routes.py, database.py, models.py

CMD ["python", "-m", "app"]   # Sanic на 8001
