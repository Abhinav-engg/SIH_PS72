.PHONY: install dev-frontend dev-backend test-ml seed-data build-frontend docker-dev

install:
	cd frontend && npm install

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

test-ml:
	python3 ml/src/evaluate.py

seed-data:
	python3 scripts/download_sample_data.py

build-frontend:
	cd frontend && npm run build

docker-dev:
	cd backend && docker compose up -d
