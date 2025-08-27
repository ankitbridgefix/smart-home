FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Run apt-get update && apt-get install -y netcat gcc postgresql libpq-dev
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

EXPOSE 8000

# CMD ["bash", "-lc", "python manage.py collectstatic --noinput || true && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"]