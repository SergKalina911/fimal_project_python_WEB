# fimal_project_python_WEB

Фінальний проект курсу Python_WEB. Обучение в GoIT

# 📸 PhotoShare API

PhotoShare — REST API на **FastAPI + SQLAlchemy + Alembic**, який реалізує:

- Авторизацію через JWT (access/refresh токени)
- Ролі користувачів: User, Moderator, Admin
- CRUD для фото, коментарів, тегів
- Завантаження фото у **Cloudinary** та трансформація фото
- Генерацію QR‑кодів
- Контейнеризацію через **Docker + Docker Compose**
- Міграції бази даних через **Alembic** в контейнері
- Swagger документацію (/docs)
- Тестування через Pytest в контейнері
- Деплой застосунку на Render.com - https://final-project-python-web.onrender.com/docs

---

## 🚀 Запуск проєкту

### 1. Клонування репозиторію

```bash
git clone https://github.com/your-repo/fimal_project_python_WEB.git
cd fimal_project_python_WEB
```

### 2. Налаштування .env

У репозиторії є файл `.env.example`.  
Він показує, які змінні середовища потрібні для роботи проєкту на локальному хості, але містить лише **шаблонні значення**.

#### Що треба зробити:

    1. Скопіювати `.env.example` → створити власний файл `.env` у корені проєкту.
    2. Замінити значення власними значеннями

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

- API буде доступне на: http://localhost:8000
- Postgres — на порту 5432

---

## 🗄️ Міграції Alembic

### Створення нової міграції

```bash
docker-compose run app alembic revision --autogenerate -m "Initial migration"
```

### Застосування міграцій

```bash
docker-compose run app alembic upgrade head
```

---

## 📂 Структура проєкту

```text
fimal_project_python_WEB/
│
├── app/                        # Основний код застосунку FastAPI
│   ├── __init__.py             # Робить папку app Python-пакетом
│   ├── main.py                 # Точка входу FastAPI (створення app, підключення маршрутів)
│   │
│   ├── core/                   # Базові налаштування та інфраструктура
│   │   ├── config.py           # Конфігурація (налаштування з .env через Pydantic)
│   │   ├── database.py         # Підключення до БД, створення engine та session
│   │   └── security.py         # Логіка JWT, хешування паролів, перевірка ролей
│   │
│   ├── models/                 # ORM-моделі SQLAlchemy
│   │   ├── __init__.py         # Імпорти моделей для зручності
│   │   ├── user.py             # Модель користувача (email, username, role, active)
│   │   ├── photo.py            # Модель фото (опис, url, owner, теги)
│   │   ├── comment.py          # Модель коментаря (text, created_at, updated_at)
│   │   └── tag.py              # Модель тегу (унікальне ім’я)
│   │
│   ├── repositories/           # Робота з БД через ORM
│   │   ├── user_repo.py        # CRUD для користувачів
│   │   ├── photo_repo.py       # CRUD для фото
│   │   └── comment_repo.py     # CRUD для коментарів
│   │
│   ├── routes/                 # REST API маршрути
│   │   ├── auth.py             # Реєстрація, логін, JWT
│   │   ├── users.py            # CRUD для користувачів, профіль
│   │   ├── photos.py           # CRUD для фото, теги, трансформації
│   │   ├── comments.py         # CRUD для коментарів
│   │   └── tags.py             # CRUD для тегів
│   │
│   ├── schemas.py              # Pydantic-схеми для валідації та серіалізації
│   │
│   └── services/               # Зовнішні сервіси
│       ├── cloudinary_service.py # Завантаження та трансформації фото через Cloudinary
│       └── qr_service.py         # Генерація QR-кодів для трансформованих фото
│
├── migrations/                 # Alembic міграції для БД
│
├── tests/                      # Тести
│
│
├── Dockerfile                  # Інструкції для створення Docker-образу
├── docker-compose.yml          # Сервіси app + db, мережі та томи
├── .env                        # Налаштування для продакшн (Postgres, JWT) - створюється окремо для деплою чи локальному використанню
├── .env.test                   # Налаштування для тестів (SQLite in-memory)
├── .env.example                # Шаблон для работи на локальному хості
├── .env.render.example         # Шаблон для деплою
├── pytest.ini                  # Конфіг для pytest (покриття >90%)
├── alembic.ini                 # Конфіг Alembic
├── pyproject.toml              # Залежності (poetry)
├── poetry.lock                 # Зафіксовані версії залежностей
├── README.md                   # Документація по запуску та деплою
├── LICENSE                     # Ліцензія проєкту
└── NFR.md                      # Нефункціональні вимоги


```

---

## 🔑 Ролі та права

```text
| Дія                                  | User      | Moderator                   | Admin         |
| -------------------------------------| ----------| ----------------------------| --------------|
| **Фото**                                                                                       |
| Завантажити/редагувати/видалити фото | ✅ (свої) | ✅ (свої)                  | ✅ (будь‑які) |
| Додати/замінити/видалити теги        | ✅ (свої) | ✅ (свої)                  | ✅ (будь‑які) |
| Модерація фото                       | ✅ (свої) | ✅ (свої)                  | ✅ (будь‑які) |
| **Коментарі**                                                                                  |
| Створити коментар                    | ✅        | ✅                         | ✅            |
| Редагувати коментар                  | ✅ (свій) | ✅ (свій)                  | ✅ (свій)     |
| Видалити коментар                    | ❌        | ✅ (будь‑які, крім адміна) | ✅ (будь‑які) |
| **Теги (глобальні)**                                                                           |
| Створити тег                         | ❌        | ❌                         | ✅            |
| Перегляд списку тегів                | ✅        | ✅                         | ✅            |
| Видалити тег                         | ❌        | ❌                         | ✅            |
| **Користувачі**                                                                                |
| Перегляд свого профілю               | ✅        | ✅                         | ✅            |
| Оновлення свого профілю              | ✅        | ✅                         | ✅            |
| Перегляд чужого профілю              | ❌        | ❌                         | ✅            |
| Оновлення чужого профілю             | ❌        | ❌                         | ❌            |
| Зміна ролі                           | ❌        | ❌                         | ✅            |
| Бан/розбан                           | ❌        | ❌                         | ✅            |

```

## 📂 Основні ендпоінти

### Auth

- POST /auth/signup — реєстрація
- POST /auth/login — логін

### Users

- GET /users/{id} — перегляд профілю
- PUT /users/{id} — оновлення профілю
- PUT /users/{id}/role — зміна ролі (Admin)
- PUT /users/{id}/ban — бан користувача (Admin)
- PUT /users/{id}/unban — розбан користувача (Admin)

### Photos

- PPOST /photos/ — завантаження фото
- PUT /photos/{id} — оновлення опису + замінює всі теги
- POST /photos/{id}/tags — додає нові теги без видалення
- DELETE /photos/{id}/tags/{tag_id} — видалення тегу з фото
- DELETE /photos/{id} — видалення фото
- PUT /photos/{id}/moderate — модерація фото (Moderator/Admin)
- GET /photos/user/{user_id} — фото користувача

### Comments

- POST /comments/ — створення коментаря
- GET /comments/{id} — отримати коментар
- PUT /comments/{id} — редагування (тільки автор)
- DELETE /comments/{id} — видалення (Moderator/Admin)

### Tags

- POST /tags/ — створення тегу (Admin)
- GET /tags/ — список тегів
- DELETE /tags/{id} — видалення тегу (Admin)

---

## 📌 Приклади запитів

Створення фото

```bash
curl -X POST http://localhost:8000/photos/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@test.jpg" \
  -F "description=Моє фото" \
  -F "tag_names=travel,nature"
```

Оновлення фото (замінює теги)

```bash
curl -X PUT http://localhost:8000/photos/6 \
  -H "Authorization: Bearer <TOKEN>" \
  -F "description=Оновлений опис" \
  -F "tag_names=newtag1,newtag2"
```

Додавання тегів

```bash
curl -X POST http://localhost:8000/photos/6/tags \
  -H "Authorization: Bearer <TOKEN>" \
  -d '["extra","fun"]'
```

Створення коментаря

```bash
curl -X POST http://localhost:8000/comments/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"photo_id": 6, "text": "Класне фото!"}'
```

Видалення коментаря (Moderator/Admin)

```bash
curl -X DELETE http://localhost:8000/comments/21 \
  -H "Authorization: Bearer <TOKEN>"
```

---

## 📌 Non-Functional Requirements (NFR)

- Performance: оптимізовані запити до БД, асинхронний FastAPI.
- Reliability: Alembic для керування схемою, Docker для відтворюваності.
- Security: JWT токени, bcrypt для паролів, .gitignore для конфігів.
- Usability: чітка структура роутів, документація OpenAPI (/docs).
- Scalability: можливість додати нові сервіси (наприклад, кеш Redis).
- Maintainability: модульна структура, розділення core/repositories/routes/services.

---

## 🛠️ Використані технології

- FastAPI
- SQLAlchemy (async)
- Alembic
- Postgres
- Docker + Docker Compose
- Cloudinary
- qrcode
- JWT (python-jose)
- Passlib (bcrypt)

---

## 🧪 Тестування

### Типи тестів

- Модульні тести (unit tests) — перевіряють окремі репозиторії та сервіси напряму, без запуску FastAPI‑app і
  без реальної БД чи Cloudinary.
- Всі зовнішні залежності (БД, Cloudinary, QR‑сервіс) замінені на моки (AsyncMock, monkeypatch).

### Запуск тестів

#### Запустити всі модульні тести

```bush
  docker-compose run app poetry run pytest
```

### Структура тестів

```text
tests/
  test_auth_routes_unit.py     # маршрути авторизації
  test_auth_unit.py            # створення користувачів, ролі, токени
  test_ban_unit.py             # логіка бану/розбану
  test_cloudinary_unit.py      # завантаження та трансформації фото (mock Cloudinary)
  test_comment_repo_unit.py    # CRUD для коментарів у репозиторії
  test_comments_routes_unit.py # маршрути коментарів
  test_comments_unit.py        # логіка коментарів, таймстемпи
  test_main_unit.py            # точка входу FastAPI
  test_photo_repo_unit.py      # CRUD для фото у репозиторії
  test_photo_transform_unit.py # трансформації фото
  test_photos_routes.py        # інтеграційні тести для фото
  test_photos_routes_unit.py   # маршрути фото
  test_photos_unit.py          # логіка фото, обмеження тегів
  test_qr_unit.py              # генерація QR-кодів
  test_roles_unit.py           # перевірка ролей користувачів
  test_schemas_unit.py         # Pydantic-схеми
  test_security_unit.py        # JWT, хешування паролів
  test_tag_repo_unit.py        # CRUD для тегів у репозиторії
  test_tags_limit_unit.py      # обмеження кількості тегів
  test_tags_routes_unit.py     # маршрути тегів
  test_tags_unit.py            # логіка тегів
  test_user_repo_unit.py       # CRUD для користувачів у репозиторії
  test_users_routes_unit.py    # маршрути користувачів
  test_users_unit.py           # логіка користувачів, бан/розбан

```

---

## ☁️ Deployment на Render

1. Реєстрація та створення сервісу

- Зареєструйтесь на Render.
- Створіть новий Web Service → вибери свій GitHub‑репозиторій.
- Виберіть Runtime: Docker (бо ми використовуємо Dockerfile).
- Регіон: Frankfurt (щоб збігалося з базою).

2. Створення бази даних

- У Render → New → PostgreSQL.
- Назвіть базу, наприклад photoshare-db.
- Render згенерує:
  - Host
  - Port
  - Database
  - Username
  - Password
- Ці дані внесіть у env.render.example

3. Налаштування env.render.example
   Відредагуйте файл .env.render.example локально з креденшіалами Render.
   Обов’язково додайте SSL‑параметри в кінці DATABASE_URL та SYNC_DATABASE_URL (приклад):

```env
    DATABASE_URL=postgresql+asyncpg://photoshare_db_u5s0_user:REAL_PASSWORD@dpg-daauakpsrm7s738ka1q0-a.frankfurt-postgres.render.com:5432/photoshare_db_u5s0?ssl=require
    SYNC_DATABASE_URL=postgresql+psycopg2://photoshare_db_u5s0_user:REAL_PASSWORD@dpg-daauakpsrm7s738ka1q0-a.frankfurt-postgres.render.com:5432/photoshare_db_u5s0?sslmode=require

    POSTGRES_DB=photoshare_db_u5s0
    POSTGRES_USER=photoshare_db_u5s0_user
    POSTGRES_PASSWORD=REAL_PASSWORD
    POSTGRES_HOST=dpg-daauakpsrm7s738ka1q0-a.frankfurt-postgres.render.com
    POSTGRES_PORT=5432
```

    ⚠️ Render вимагає SSL: ?ssl=require для asyncpg і ?sslmode=require для psycopg2.

4. Локальний запуск і міграції
   - Перейменуйте .env.render.example у .env.
   - Запустіть:

```bash
docker-compose up --build
docker-compose exec app poetry run alembic upgrade head
```

- Це проганяє всі міграції на Render‑базу.

5. Environment Variables у Render

- У сервісі final_project_python_WEB → Environment.
- Додайте ті самі змінні '(DATABASE*URL, SYNC_DATABASE_URL, POSTGRES\*, SECRET_KEY, CLOUDINARY, EMAIL*\*).'
- Збережіть → натисніть Save, rebuild, and deploy.

6. Перевірка деплою

- Render покаже URL, наприклад:
  https://final-project-python-web.onrender.com

- Swagger документація доступна на:
  https://final-project-python-web.onrender.com/docs

- Перевірте /auth/signup → має створювати користувача і повертати токени.

### ⚡ Таким чином:

- Локально ви тестуєте міграції через .env.
- На Render прописуєте ті самі змінні у Environment.
- Після деплою бекенд працює з базою, а всі ендпоінти доступні через публічний URL.

---

## Оригінал завдання

### Технічне завдання на створення застосунку “PhotoShare” (REST API)

                  Основний функціонал для REST API виконаний на FastAPI

#### Аутентифікація

1. Створюємо механізм аутентифікації. Використовуємо JWT токени
2. Користувачі мають три ролі. Звичайний користувач, модератор та адмінстратор. Перший користувач в системі завжди адміністратор
3. Для реалізації різних рівнів доступу (звичайний користувач, модератор і адміністратор) ми можемо використовувати декоратори FastAPI для перевірки токена і ролі користувача.

#### Робота с світлинами

1. Користувачі можуть завантажувати світлини з описом (POST).
2. Користувачі можуть видаляти світлини (DELETE).
3. Користувачі можуть редагувати опис світлини (PUT).
4. Користувачі можуть отримувати світлину за унікальним посиланням (GET).
5. Можливість додавати до 5 тегів під світлину. Додавання тегу не обов'язкове при завантаженні світлини.
6. Теги унікальні для всього застосунку. Тег передається на сервер по імені. Якщо такого тега не існує, то він створюється, якщо існує, то для світлини береться існуючий тег з такою назвою.
7. Користувачі можуть виконувати базові операції над світлинами, які дозволяє сервіс Cloudinary (https://cloudinary.com/documentation/image_transformations). Можливо вибрати обмежений набір трансформацій над світлинами для свого застосунку з Cloudinary.
8. Користувачі можуть створювати посилання на трансформоване зображення для перегляду світлини в вигляді URL та QR-code (https://pypi.org/project/qrcode/). Операція POST, оскільки створюється окреме посилання на трансформоване зображення, яке зберігається в базі даних
9. Створені посилання зберігаються на сервері і через мобільний телефон ми можемо відсканувати QR-code та побачити зображення
10. Адміністратори можуть робить всі CRUD операції зі світлинами користувачів

#### Коментування

1. Під кожною світлиною, є блок з коментарями. Користувачі можуть коментувати світлину один одного
2. Користувач може редагувати свій коментар, але не видаляти
3. Адміністратори та модератори можуть видаляти коментарі.
4. Для коментарів обов'язково зберігати час створення та час редагування коментаря в базі даних. Для реалізації функціональності коментарів, ми можемо використовувати відношення "один до багатьох" між світлинами і коментарями в базі даних. Для тимчасового маркування коментарів, використовувати стовпці "created_at" і "updated_at" у таблиці коментарів.

#### Додатковий функціонал

1. Створити маршрут для профіля користувача за його унікальним юзернеймом. Повинна повертатися вся інформація про користувача. Ім’я, коли зареєстрований, кількість завантажених фото тощо
2. Користувач може редагувати інформацію про себе та бачити інформацію про себе. Це мають бути різні маршрути з профілем користувача. Профіль для всіх користувачів, а інформація для себе - це те, що можна редагувати
3. Адміністратор може робити користувачів неактивними (банити). Неактивні користувачі не можуть заходити в застосунок

#### Додатково по можливості реалізувати наступні задачі, якщо дозволяє час.

1. Реалізувати механізм виходу користувача з застосунку через logout. Access token повинен бути доданий на час його існування в чорний список.
2. Рейтинг

● Користувачі можуть виставляти рейтинг світлині від 1 до 5 зірок. Рейтинг обчислюється як середнє значення оцінок всіх користувачів.
● Можна тільки раз виставляти оцінку світлині для користувача.
● Не можливо оцінювати свої світлини.
● Модератори та адміністратори можуть переглядати та видаляти оцінки користувачів.

3. Пошук та фільтрація

● Користувач може здійснювати пошук світлин за ключовим словом або тегом. Після пошуку користувач може відфільтрувати результати за рейтингом або датою додавання.
● Модератори та адміністратори можуть виконувати пошук та фільтрацію за користувачами, які додали світлини.

#### Після виконання основного функціоналу

1. Покрити застосунок модульними тестами, добитись покриття більш ніж на 90 %
2. Виконайте деплой застосунку для якогось хмарного сервісу на ваш вибір. Рекомендація Koyeb (https://app.koyeb.com/auth/signin) , Fly.io (https://fly.io/app/sign-in)

#### Критерії прийому

1. Web-застосунок реалізований на фреймворку FastAPI.
2. Проєкт має бути збережений в окремому репозиторії та бути загальнодоступним (GitHub, GitLab або BitBucket).
3. Для зберігання інформації про користувачів, світлини та коментарі використовувати PostgreSQL. Для взаємодії з базою даних, використовувати бібліотеку SQLAlchemy, яка надає ORM-функціональність для роботи з базою даних.
4. Проєкт містить докладну інструкцію щодо встановлення та використання.
5. Проєкт повністю реалізує вимоги, описані в завданні.
6. Проєкт має повну Swagger документацію
7. Створення Dockerfile: Розробіть Dockerfile для створення образу Docker, який дозволить розміщувати та запускати нашу програму в контейнеризованому середовищі. Dockerfile має включати всі необхідні інструкції для створення образу, включаючи вибір базового образу, копіювання вихідного коду програми до контейнера, встановлення необхідних залежностей та визначення команди для запуску програми.
8. Використання Docker Compose: Інтегруйте інструмент Docker Compose для спрощення процесу розгортання та управління нашим проєктом у середовищі Docker. Створіть файл docker-compose.yml, який описує послуги, мережі та томи, необхідні для проекту. Файл повинен дозволяти запускати весь проєкт за допомогою однієї команди docker-compose up, автоматизуючи створення та запуск необхідних Docker контейнерів.
