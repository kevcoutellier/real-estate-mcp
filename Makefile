# Makefile pour MCP Immobilier

.PHONY: install test run clean

# Installation
install:
	python -m venv venv
	./venv/bin/pip install -r requirements.txt

# Tests
test:
	python test_mcp.py

# Lancement
run:
	python src/main.py

# Nettoyage
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.pyc
	rm -rf logs/

# Mise à jour des dépendances
update:
	./venv/bin/pip install --upgrade -r requirements.txt

# Vérification du code
lint:
	./venv/bin/python -m flake8 src/
	./venv/bin/python -m mypy src/

# Documentation
docs:
	echo "📖 Documentation MCP Immobilier"
	echo "================================"
	echo "Commandes disponibles:"
	echo "  make install  - Installation"
	echo "  make test     - Tests"
	echo "  make run      - Lancement"
	echo "  make clean    - Nettoyage"