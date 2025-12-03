# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем зависимости для psycopg2 и т.д.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Сначала копируем только зависимости, чтобы кешировать слои
# Если у вас зависимости в requirements.txt:
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Затем копируем исходники
COPY . /app

# Переменные окружения по умолчанию (можно переопределить в docker-compose)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Открываем порт для uvicorn
EXPOSE 8000

# Команда запуска приложения
# Если ваша точка входа app/main.py и объект приложения называется app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
