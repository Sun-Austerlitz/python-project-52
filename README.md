[![Actions Status](https://github.com/Sun-Austerlitz/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Sun-Austerlitz/python-project-52/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Sun-Austerlitz_python-project-52&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Sun-Austerlitz_python-project-52)

https://python-project-52-73nf.onrender.com/

---

## Описание

Менеджер задач — это приложение, предназначенное для управления и планирования задач с возможностью работы нескольких пользователей. Каждый пользователь может:

- Создавать и редактировать задачи.
- Присваивать задачам статусы и метки.
- Удалять свои задачи.
- Управлять своим профилем (регистрация, редактирование, удаление)

Приложение поддерживает авторизацию, а также фильтрацию задач по различным параметрам.

---

## Запуск 

### 1. Клонировать репозиторий:
```bash
git clone https://github.com/Sun-Austerlitz/python-project-52.git
cd python-project-52
```
### 2. Установка зависимости и применение миграции для бд

```bash
make build 
```

Для локального запуска дополнительных настроек не требуется. В продакшене необходимо задать переменную окружения `SECRET_KEY`:

```bash
export SECRET_KEY=your-production-secret-key
```

### 3. Запуск приложения
```bash
make render-start
```

---

## Используемые технологии

- **Django** — Python фреймворк для веб-разработки
- **Bootstrap 5** — css для интерфейса
- **Gunicorn + Render** — развертывание