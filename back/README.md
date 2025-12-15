# FastAPI Robot Control System

Миграция Django проекта на FastAPI с использованием SQLAlchemy.

## Структура проекта

```
back_fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # Главный файл приложения
│   ├── database.py          # Настройка БД и SQLAlchemy
│   ├── models/              # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── robot.py
│   │   ├── sensor.py
│   │   ├── battery.py
│   │   └── distance.py
│   ├── schemas/             # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── robot.py
│   │   └── sensor.py
│   ├── routers/             # FastAPI роутеры
│   │   ├── __init__.py
│   │   └── core.py
│   ├── mqtt/                # MQTT интеграция
│   │   ├── __init__.py
│   │   ├── app_config.py
│   │   ├── commands_const.py
│   │   └── service.py
│   └── enums/               # Перечисления
│       ├── __init__.py
│       └── sensor_type_enum.py
├── templates/               # Jinja2 шаблоны
│   └── core/
│       ├── base.html
│       ├── index.html
│       ├── robot.html
│       ├── create.html
│       └── bluetooth.html
├── staticfiles/             # Статические файлы (CSS, JS, изображения)
│   └── core/
│       ├── css/
│       ├── js/
│       └── images/
├── requirements.txt
└── README.md
```

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Скопируйте статические файлы из `back/staticfiles` в `back_fastapi/staticfiles`:
   ```bash
   python copy_static.py
   ```
   Или вручную скопируйте папку `back/staticfiles` в `back_fastapi/staticfiles`

3. Запустите приложение:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Или используйте:
```bash
python -m uvicorn app.main:app --reload
```

## Основные изменения по сравнению с Django

1. **ORM**: Django ORM → SQLAlchemy
2. **Валидация**: Django Forms → Pydantic схемы
3. **Роутинг**: Django URLs → FastAPI роутеры
4. **Шаблоны**: Django Templates → Jinja2 (совместимый синтаксис)
5. **Статические файлы**: Django staticfiles → FastAPI StaticFiles

## API Endpoints

- `GET /` - Главная страница со списком роботов
- `GET /robot/{robot_id}` - Страница детальной информации о роботе
- `GET /robot_create/` - Форма создания робота
- `POST /robot_create/` - Создание нового робота
- `GET /robot_delete/{robot_id}` - Удаление робота
- `GET /robot_bluetooth/{robot_id}` - Переключение в режим ручного управления
- `GET /sensor_data/?sensor_type={type}` - API для получения данных датчиков
- `GET /robot_data/?robot={id}` - API для получения данных робота
- `POST /publish/` - Публикация сообщения через MQTT

## База данных

Проект использует SQLite базу данных (`db.sqlite3`). При первом запуске таблицы создаются автоматически.

Для миграции данных из Django проекта можно использовать скрипт миграции или экспорт/импорт данных.

## MQTT

MQTT клиент автоматически запускается при старте приложения и подключается к брокеру:
- Сервер: `185.152.81.104`
- Порт: `1883`
- Топик: `esp8266/sensor/`

## Примечания

- Шаблоны адаптированы для работы с Jinja2 (убраны Django-специфичные теги)
- Статические файлы должны быть скопированы из `back/staticfiles` в `back_fastapi/staticfiles`
- База данных SQLite будет создана автоматически при первом запуске

