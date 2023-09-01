docker compose up -d --build --force-recreate
docker rmi $(docker images -f "dangling=true" -q)