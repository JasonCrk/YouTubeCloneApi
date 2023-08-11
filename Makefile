dev:
	docker compose -f docker-compose-dev.yml run -d

stop:
	docker compose -f docker-compose-dev.yml stop

migrate:
	docker exec -it youtube_clone_api python manage.py migrate

all-tests:
	docker exec -it youtube_clone_api python manage.py test

logs:
	docker logs youtube_clone_api -f
