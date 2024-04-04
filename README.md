# carebot
CS 495 Senior Design Project

## Prerequisites
1. Docker

## Setup
1. Clone the repository.
2. Create a file called `.env` in the root of the repository.
3. Add the following text to `.env`. Place your OpenAI API key between the quotation marks. `OPENAI_API_KEY=""`
4. Add `DEBUG="False"` to `.env`.
5. Add `INSECURE_FLAG=""` to `.env`.

## Hosting Locally with Docker
1. If you have not ever run this command, run `docker-compose build`.
2. Run `docker-compose up`.
3. In your web browser, go to [localhost:80](localhost:80).

## Making Changes to Models
If you make any changes to the files in or structure of the Django app, most changes will update automatically. Consult the Django documentation for commands to generate static files. Use these commands if you alter `models.py` or any static files.
1. Run `docker-compose build`.
2. Run `docker-compose up`.
