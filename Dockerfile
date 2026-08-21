FROM python:3.13-slim

WORKDIR /app

# Оновлюємо pip і ставимо poetry
RUN pip install --upgrade pip && pip install poetry

# Копіюємо файли залежностей
COPY pyproject.toml poetry.lock* ./

# Встановлюємо всі залежності (з pyproject.toml)
RUN poetry install --no-root

# Копіюємо весь код
COPY . .

# Запускаємо uvicorn через poetry, щоб він бачив fastapi та інші пакети
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
