# Установка зависимостей
FROM python:3.10

# Установка pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

# Копирование Pipfile и Pipfile.lock
WORKDIR /app
COPY Pipfile* /app/

EXPOSE 8000

# Копирование приложения
COPY . /app

# Установка зависимостей с помощью pipenv

# Установка зависимостей с помощью pipenv
RUN pipenv install --deploy --ignore-pipfile

# Добавление переменной окружения PYTHONPATH
# ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# Запуск приложения

# CMD ["sh", "-c", "pipenv run python3 main.py"]
CMD ["pipenv", "run", "python3", "main.py"]
