# carebot
CS 495 Senior Design Project

## Prerequisites
1. Docker

## Setup
1. Clone the repository.
2. Create a file called `.env` in the root of the repository.
3. Add the following text to `.env`. Place your OpenAI API key between the quotation marks. `OPENAI_API_KEY=""`

## Hosting Locally with Docker
1. If you have made any changes to the files, you must run this command to create the Docker image again: `docker-compose build.`
2. Run `docker-compose run`
3. In your web browser, go to [localhost:8000](localhost:8000).

## Making Changes to Models
If you make any changes to the files in or structure of the Django app, most changes will update automatically. Consult the Django documentation for commands to generate static files. Use these commands if you alter `models.py`.
1. Run `python carebot/manage.py makemigrations chat` in your pipenv.
2. Run `python carebot/manage.py migrate chat` in your pipenv.
