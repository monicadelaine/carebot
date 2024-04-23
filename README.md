# carebot

CS 495 Senior Design Project

## Prerequisites and Paid Services

1. [Docker](https://docs.docker.com/engine/install/)
2. [Docker Compose](https://docs.docker.com/compose/)
3. [OpenAI API key](https://platform.openai.com/docs/introduction) for ChatGPT v3.5 (paid)

## Setup

1. Clone the repository.
2. Create a file called `.env` in the root of the repository.
3. Add `OPENAI_API_KEY="[your OpenAI API key]"` to `.env`.
4. Add `DEBUG="True"` to `.env`.
5. Add `INSECURE_FLAG=""` to `.env`.
6. Add `SECRET_KEY="[your secret key]"` to `.env`.

## Hosting Locally with Docker

1. If you have not ever run this command, run `docker compose build`.
2. Run `docker compose up`.
3. In your web browser, go to [localhost](localhost).

## Making Changes

If you make any changes to the files in or structure of the Django app, most changes will update automatically. Consult the [Django documentation](https://docs.djangoproject.com/en/5.0/howto/static-files/) for commands to generate static files. Use these commands if you alter `models.py` or any static files. Rebuild the Docker container if you make any changes to Docker files or the Python installation.

1. Run `docker compose build`.
2. Run `docker compose up`.
