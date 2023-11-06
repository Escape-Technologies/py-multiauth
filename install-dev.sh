#!/bin/sh

echo -e "\n\n\n\n\n---- Installing Python Poetry ----"
pip install -U pip
pip install -U poetry
poetry config virtualenvs.in-project true

echo -e "\n\n\n\n\n---- Installing Python dependencies ----"
poetry install

echo -e "\n\n\n\n\n---- Git hooks init (using mookme) ----"
npm install
npx mookme init --only-hook --skip-types-selection

echo -e "\n\n\n\n\n---- Your working directory is all set :) ----"
