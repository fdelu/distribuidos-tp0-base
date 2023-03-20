docker-image:
	docker build -t "test_server:latest" .
.PHONY: docker-image

run: docker-image
	docker compose -f docker-compose.yaml up --build --attach=test_server
	docker compose -f docker-compose.yaml down
.PHONY: run
