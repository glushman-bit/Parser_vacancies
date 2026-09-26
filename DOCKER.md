```
deploy:
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.2.2
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /var/www/parser_vacancies
            docker compose pull web
            docker compose up -d --force-recreate web
            docker compose up -d --force-recreate nginx
            docker compose ps
```

Что здесь происходит
 - needs: build — деплой запускается только после успешной сборки.
 - appleboy/ssh-action — подключается к серверу по SSH.
 - docker compose pull web — скачивает новый образ из Docker Hub.
 - docker compose up -d --force-recreate web — пересоздаёт приложение.
 - docker compose up -d --force-recreate nginx — пересоздаёт Nginx, чтобы он заново обнаружил web.
 - docker compose ps — показывает состояние контейнеров.

==========================================================

Проверка Web после Deploy:
```textmate
script: |
  cd /var/www/parser_vacancies

  docker compose pull web

  docker compose up -d --force-recreate web

  echo "Waiting for web container..."

  for i in {1..30}; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' parser_vacancies-web-1 2>/dev/null || true)

    echo "Health status: $STATUS"

    if [ "$STATUS" = "healthy" ]; then
      echo "Web is healthy"
      break
    fi

    if [ "$STATUS" = "unhealthy" ]; then
      echo "Web is unhealthy"
      docker compose logs --tail=50 web
      exit 1
    fi

    sleep 2
  done

  if [ "$STATUS" != "healthy" ]; then
    echo "Web did not become healthy in time"
    docker compose logs --tail=50 web
    exit 1
  fi

  docker compose up -d --force-recreate nginx

  docker compose ps
```

Что здесь происходит

После:
```
docker compose up -d --force-recreate web
```
мы не сразу пересоздаём Nginx.

Сначала проверяем:
```
starting
   ↓
healthcheck
   ↓
healthy?
```
Цикл:
```
for i in {1..30}
```
даёт максимум примерно 60 секунд на запуск.

Если всё хорошо:
```
Health status: starting
Health status: starting
Health status: healthy
Web is healthy
```
→ продолжаем deployment.

Если приложение сломалось:
```
Health status: unhealthy
Web is unhealthy
```
→ выводим последние логи web и:

exit 1

GitHub Actions получает ненулевой код и показывает deployment как failed.

Почему Nginx создаём после healthy

Это тоже важно.

Получается:
```
pull image
    ↓
recreate web
    ↓
web healthy
    ↓
recreate nginx
    ↓
готово
```
Так мы не заставляем Nginx подключаться к приложению в момент, когда Gunicorn ещё запускается.

==============================================

```textmate
script: |
    cd /var/www/parser_vacancies
    
    IMAGE_TAG="${{ github.sha }}"
    
    if grep -q '^IMAGE_TAG=' .env; then
      sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${IMAGE_TAG}/" .env
    else
      echo "IMAGE_TAG=${IMAGE_TAG}" >> .env
    fi
    
    docker compose pull web
```

Что здесь происходит

GitHub Actions подставляет SHA текущего коммита:
```
IMAGE_TAG="${{ github.sha }}"
```
Например:
```
fae1386352d175de93ce43bf9624094647320284
```
Затем:
```
grep -q '^IMAGE_TAG=' .env
```
проверяет, есть ли уже IMAGE_TAG.

Если есть:
```
IMAGE_TAG=старый_SHA
```
то:
```
sed -i ...
```
заменит только эту строку.

Если строки нет:
```
echo ...
```
добавит её в конец .env.

Таким образом, остальные переменные:
```
POSTGRES_HOST=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=...
POSTGRES_NAME=headhunter_drf
ALLOWED_HOSTS=...
```
останутся нетронутыми.