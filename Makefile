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

prod-save:
	@last_log=$$(ls -t logs/logs_*.txt | head -n 1); \
	if [ -n "$$last_log" ]; then \
		last_timestamp=$$(echo $$last_log | grep -oE '[0-9]{8}_[0-9]{6}'); \
		formatted_timestamp=$$(echo $$last_timestamp | sed -E 's/^([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})/\1-\2-\3 \4:\5:\6/'); \
		iso_timestamp=$$(date -d "$$formatted_timestamp" --iso-8601=seconds 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S" "$$formatted_timestamp" "+%Y-%m-%dT%H:%M:%S"); \
		sudo docker logs --since "$$iso_timestamp" api > logs/logs_$$(date +%Y%m%d_%H%M%S).txt 2>&1; \
	else \
		echo "No previous logs found. Saving full logs..."; \
		sudo docker logs api > logs/logs_$$(date +%Y%m%d_%H%M%S).txt 2>&1; \
	fi