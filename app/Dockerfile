# Базовый образ: Python 3.12 на Alpine Linux (маленький размер)
FROM python:3.12-alpine


# Переменные окружения для работы Python в Docker:
# HOME - домашняя папка пользователя (/home/fast)
# APP_HOME - папка где лежит код приложения (/home/fast/app)
# PYTHONPATH - добавляем /home/fast в пути поиска модулей (чтобы работал import app)
# PYTHONDONTWRITEBYTECODE - отключаем создание __pycache__ (не нужно в Docker)
# PYTHONUNBUFFERED - логи выводятся сразу без буферизации (для docker logs)
ENV HOME=/home/fast \
    APP_HOME=/home/fast/app \
    PYTHONPATH="$PYTHONPATH:/home/fast" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# Создаем структуру для безопасного запуска (не от root):
# - создаем папку /home/fast/app для кода
# - создаем группу fast
# - создаем пользователя fast без root прав
RUN mkdir -p $APP_HOME \
  && addgroup -S fast \
  && adduser -S fast -G fast


# Устанавливаем рабочую директорию (все команды выполняются отсюда)
WORKDIR $HOME


# Копируем файлы проекта в контейнер:
# - папку app с кодом
# - файлы конфигурации (requirements.txt, alembic.ini, .env)
COPY app app
COPY requirements.txt alembic.ini .env .


# Устанавливаем зависимости и передаем права:
# - обновляем pip до последней версии
# - устанавливаем все пакеты из requirements.txt
# - отдаем все файлы пользователю fast (чтобы он мог их читать)
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && chown -R fast:fast .


# Переключаемся на пользователя fast (безопасность!)
# Приложение будет работать от fast, а не от root
USER fast
