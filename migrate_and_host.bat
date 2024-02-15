@echo off

REM Set up and run migrations
pipenv run python carebot/manage.py makemigrations
pipenv run python carebot/manage.py migrate

REM Start the development server
pipenv run python carebot/manage.py runserver
