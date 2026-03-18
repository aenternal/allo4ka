# Allo4ka 2.0 (safe moderation edition)

> Перезапуск проекта в сторону мультиплатформенного бота-модератора для VK и Telegram.

## Что реализовано

- Интеграция с **VK** и **Telegram** через единый сервис обработки входящих сообщений.
- Вынесенная генерация голосовых ответов в фоновые задачи (**Celery** + Redis).
- Кэширование сгенерированных голосовых файлов по тексту ответа.
- База данных с:
  - триггерами (слово/фраза + платформа + флаг активности),
  - текстовыми ответами,
  - 4-составными фрагментами ответов,
  - кэшем аудио.
- Админ API (FastAPI) для CRUD-настроек триггеров и ответов.

## Важное замечание по безопасности

В этой версии проект ориентирован на **модерацию и деэскалацию**. Конфигурация ответов должна оставаться в рамках правил платформ и закона.

## Структура

```text
app/
  api/
    admin.py
  bots/
    telegram_bot.py
    vk_bot.py
  tasks/
    celery_app.py
    jobs.py
  services/
    message_router.py
    response_builder.py
    tts.py
  config.py
  db.py
  models.py
docker-compose.yml
Dockerfile
run_admin.py
run_bots.py
```

## Запуск через Docker Compose (рекомендуется)

1. Создай `.env`:

```bash
cp .env.example .env
```

2. Заполни токены:
- `TELEGRAM_BOT_TOKEN`
- `VK_GROUP_TOKEN`

3. Подними всё окружение:

```bash
docker compose up --build
```

Будут запущены сервисы:
- `db` (PostgreSQL)
- `redis`
- `init-db` (одноразовая инициализация таблиц)
- `admin` (FastAPI на `:8000`)
- `worker` (Celery)
- `bots` (VK + Telegram polling)

## Локальный запуск без Docker

### 1) Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) Настройка окружения

```bash
cp .env.example .env
```

### 3) Инициализация БД

```bash
python run_admin.py --init-db
```

### 4) Запуск сервисов

В разных терминалах:

```bash
python run_admin.py
```

```bash
celery -A app.tasks.celery_app.celery_app worker -l info
```

```bash
python run_bots.py
```

## Админ API

После запуска FastAPI:

- `GET /health`
- `POST /triggers`
- `GET /triggers`
- `PATCH /triggers/{id}`
- `POST /responses`
- `GET /responses`
- `POST /fragments`
- `GET /fragments`

Фрагменты состоят из 4 частей (`part1..part4`) и используются для сборки сообщений.
