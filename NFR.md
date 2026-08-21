# 📌 Non-Functional Requirements (NFR)

Документ описує нефункціональні вимоги до проєкту **PhotoShare**.

---

## 🔹 Performance

- Асинхронний **FastAPI** для високої продуктивності.
- Оптимізовані SQLAlchemy‑запити.
- Використання кешування (можливість інтеграції Redis).
- Мінімізація блокуючих операцій.

---

## 🔹 Reliability

- **Alembic** для керування схемою БД.
- **Docker Compose** для відтворюваного середовища.
- Автоматичний перезапуск контейнерів (`restart: always`).
- Логування через стандартні інструменти Python та Alembic.

---

## 🔹 Security

- Авторизація через **JWT** (access/refresh токени).
- Хешування паролів через **bcrypt** (Passlib).
- Використання `.gitignore` для приховування конфігів.
- Зберігання секретів у `.env`, а не в коді.

---

## 🔹 Usability

- Чітка структура роутів (`auth`, `users`, `photos`, `comments`).
- Документація OpenAPI доступна за `/docs`.
- Приклади API у README.md.
- Зручний запуск через Docker.

---

## 🔹 Scalability

- Модульна архітектура (core, repositories, routes, services).
- Легка інтеграція нових сервісів (наприклад, кеш, черги RabbitMQ).
- Можливість горизонтального масштабування через Docker Swarm/Kubernetes.

---

## 🔹 Maintainability

- Розділення коду на модулі (core, models, services).
- Використання **Poetry** для керування залежностями.
- Автоматичні міграції через Alembic.
- README.md та NFR.md для документації.
