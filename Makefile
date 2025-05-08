dev-up:
	docker compose -f docker-compose.dev.yml --env-file backend/.env.dev up --build -d

dev-down:
	docker compose -f docker-compose.dev.yml --env-file backend/.env.dev down

dev-logs:
	docker logs -f --tail 1000 api_dev

dev-restart:
	docker restart api_dev

prod-up:
	docker compose -f docker-compose.prod.yml --env-file backend/.env.prod up --build -d

prod-down:
	docker compose -f docker-compose.prod.yml --env-file backend/.env.prod down

prod-logs:
	docker logs -f --tail 1000 api

prod-restart:
	docker restart api