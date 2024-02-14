# carebot
CS 495 Senior Design Project

## Prerequisites
1. Python 3.12+
2. pipenv

## Setup
1. Clone the repository.
2. Create a file called `.env` in the root of the repository.
3. Add the following text to `.env`. Place your OpenAI API key between the quotation marks. `OPENAI_API_KEY=""`
4. Set up the pipenv by running `pipenv install` in the root of your repository.
5. Enter the virtual environment by running `pipenv shell`. (To exit, type `exit`.)
6. Run `python carebot/manage.py runserver`.
7. In your web browser, go to [localhost:8000](localhost:8000).

## Making Changes
If you make any changes to the files in or structure of the Django app, most changes will update automatically. Consult the Django documentation for commands to generate static files or make migrations.
