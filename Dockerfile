FROM python:3.11-slim
WORKDIR /srv

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY anon.session .
COPY app ./app
CMD ["python", "-m", "app.main"]
