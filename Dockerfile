FROM python:3.14-slim

LABEL authors="Ivan"

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bing", "0.0.0.0:8000"]
