docker compose -f docker/mongodb.compose.yml up -d 
docker compose -f docker/rabbitmq.compose.yml up -d
docker compose -f docker/monitor.compose.yml up -d