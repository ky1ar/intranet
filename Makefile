dev-up:
	docker compose -f docker-compose.dev.yml up --build -d

dev-down:
	docker compose -f docker-compose.dev.yml down

dev-logs:
	docker logs -f backend_dev

dev-flogs:
	docker logs -f --tail 1000 backend_dev

dev-restart:
	docker restart backend_dev

prod-up:
	docker compose -f docker-compose.prod.yml up --build -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker logs -f backend