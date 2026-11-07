.PHONY: setup init-db generate-data seed export-powerbi run test lint clean docker-up docker-down

PYTHON = .venv/bin/python
PIP = .venv/bin/pip
PYTEST = .venv/bin/pytest
RUFF = .venv/bin/ruff
STREAMLIT = .venv/bin/streamlit

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	cp -n .env.example .env || true

init-db:
	$(PYTHON) scripts/init_db.py

generate-data:
	$(PYTHON) scripts/generate_synthetic_data.py

seed:
	$(PYTHON) scripts/seed_database.py

export-powerbi:
	$(PYTHON) scripts/export_powerbi_data.py

run:
	$(STREAMLIT) run app/Home.py --server.port=8501 --server.address=0.0.0.0

test:
	$(PYTEST) -v

lint:
	$(RUFF) check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down -v
