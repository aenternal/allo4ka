# Allo4ka 2.0 (safe moderation edition)

> Перезапуск проекта в сторону мультиплатформенного бота-модератора для VK и Telegram.

## Что реализовано

- Интеграция с **VK** и **Telegram** через единый сервис обработки входящих сообщений.
- Вынесенная генерация голосовых ответов в фоновые задачи (**Celery** + Redis/RabbitMQ).
- Кэширование сгенерированных голосовых файлов по тексту ответа, чтобы переиспользовать результат.
- База данных с:
  - триггерами (слово/фраза + платформа + флаг активности),
  - текстовыми ответами,
  - 4-составными фрагментами ответов,
  - кэшем аудио.
- Админ API (FastAPI) для CRUD-настроек триггеров и ответов.

---

## Важное замечание по безопасности

В этой версии проект ориентирован на **модерацию и деэскалацию**. Конфигурация ответов должна оставаться в рамках правил платформ и закона.

---

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
run_admin.py
run_bots.py
```

---

## Быстрый старт

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

Заполни:
- `DATABASE_URL`
- `TELEGRAM_BOT_TOKEN`
- `VK_GROUP_TOKEN`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

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

---

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

---

## Как работает обработка

1. Бот получает сообщение (VK/Telegram).
2. `MessageRouter` проверяет триггеры для платформы.
3. Если есть совпадение — собирается ответ:
   - либо из конкретного шаблона,
   - либо из случайной комбинации 4 фрагментов.
4. Отправляется текст.
5. В фоне ставится задача генерации голосового файла.
6. При повторе того же текста используется кэш из БД.
