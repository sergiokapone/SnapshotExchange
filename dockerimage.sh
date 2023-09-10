#!/bin/bash

# Сборка Docker-образа
docker build -t sergiokapone/snapshopexchange .

# Запуск контейнера с монтированием volumes
docker run -p 8000:8000 sergiokapone/snapshopexchange

# Отправка Docker-образа в репозиторий
# docker push sergiokapone/snapshopexchange
