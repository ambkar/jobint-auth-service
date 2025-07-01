FROM python:3.11-slim
WORKDIR /srv

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN psql
RUN CREATE ROLE jobint_user LOGIN PASSWORD 'Karen_2003' SUPERUSER;
RUN CREATE DATABASE jobint OWNER jobint_user;
RUN GRANT ALL PRIVILEGES ON DATABASE jobint TO jobint_user;

COPY app ./app
CMD ["python", "-m", "app.main"]
