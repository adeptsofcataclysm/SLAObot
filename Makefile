bot:
	python slao_bot.py

requirements:
	pip install -r requirements-dev.txt

start: requirements bot

mypy:
	mypy slao_bot.py

flake8:
	flake8 .

isort:
	isort .

check: isort flake8
