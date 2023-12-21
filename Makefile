.PHONY: setup install-poetry install-dependencies init-git-hooks

setup: install-poetry install-dependencies init-git-hooks
	@echo "\n---- Your working directory is all set :) ----"

install-poetry:
	@echo "\n---- Installing Python Poetry ----"
	pip install -U pip
	pip install -U poetry
	poetry config virtualenvs.in-project true

install-dependencies:
	@echo "\n---- Installing Python dependencies ----"
	poetry install

init-git-hooks:
	@echo "\n---- Git hooks init (using mookme) ----"
	npm install
	npx mookme init --only-hook --skip-types-selection