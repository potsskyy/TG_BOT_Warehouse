# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код в контейнер
COPY . .

# Загружаем переменные среды, если нужно
ENV PYTHONUNBUFFERED=1

# Указываем команду по умолчанию для запуска контейнера
CMD ["python", "main.py"]
