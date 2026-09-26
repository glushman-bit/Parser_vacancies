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