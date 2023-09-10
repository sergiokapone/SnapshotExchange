:: Сборка Docker-образа
docker build -t sergiokapone/SnapshopExchange .

:: Запуск контейнера с монтированием volumes
docker run -p 8000:8000 sergiokapone/SnapshopExchange

rem docker push sergiokapone/SnapshopExchange
