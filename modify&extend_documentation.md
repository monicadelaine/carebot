# Caregiver Connect Chatbot Documentation

## 3. How to Modify/Extend Software
The current version of the application is built using Docker and a Python backend, so there is no need for a compiler. 
Anytime changes are made to the project, they are often automatically updated through the running Docker image. 
If your changes are made to any static files, you create any new models, URL paths, or input forms, or any other changes are not adapted, you may need to restart the application by running `docker compose down`, `docker compose build` and `docker compose up`. 
Any changes to the construction of the project’s build protocol, including port numbers, database passwords, version numbers, and paths to files can be made within the `docker-compose.yml` file, which configures both the Carebot application and the PostgreSQL database that the application is connected to.

### 3.1. Views.py
After cloning the GitHub repository, any changes to the Chatbot itself, including OpenAI API calls, backend processing, data processing, and data/message storage can be addressed in the `views.py` file. 
This file contains the bulk of the backend processing needed to store user chat history, process user input, make OpenAI API calls, generate SQL queries, fetch data from the database, and return the data to the user. 
Any updates to the OpenAI model or a different API call can be made from the `chat_view()` function within `views.py`. 
If you would like to include additional URL views, the function that renders each corresponding view should be placed within the `views.py` file. 
Any changes to this file while the application is running should be applied automatically. If you do not see changes to the code, you can run `docker compose down`, `docker compose build` and `docker compose up` to restart the application. 
For additional documentation on the purpose of the `views.py` file and its role within the Django structure, refer to this [link](https://docs.djangoproject.com/en/5.0/topics/http/views/).

### 3.2. Urls.py
To add future pages/URL’s to the application, you can create an additional path to your desired URL within the `urls.py` file. 
You will need to include the relative path or the URL, the `views.py` function that renders the view for that URL, and a common name the URL can be referred to.
Any changes to this file while the application is running should be applied automatically. 
If you do not see changes to the code, you can run `docker compose down`, `docker compose build` and `docker compose up` to restart the application. 
For additional documentation on the purpose of the `urls.py` file and its role within the Django structure, refer to this [link](https://docs.djangoproject.com/en/5.0/topics/http/urls/).

### 3.3. Tests.py
For any additional unit tests needed for the application, you can create the necessary classes and functions for each new unit test. 
The general structure allows you to create a class for a particular file or function of the application, where each class contains a collection of functions to test a certain feature.
You can either add functions to one or multiple classes or create a new class to test a separate function of the application. 
For additional documentation on the purpose of the `tests.py` file and its role within the Django structure, refer to this [link](https://docs.djangoproject.com/en/5.0/topics/testing/).

#### 3.3.1. Running Unit Tests
To test the application with a particular test suite, you must navigate to the docker container of the application. 
While the application is running, you can either open a new terminal and run the commands `docker ps` (to list each current docker process running) and `docker exec -it <docker_container_id> /bin/bash` to create a shell within the Carebot docker container. 
Make sure to use the container ID for the Carebot container rather than the database container. 
If you are using Docker Desktop, you can simply use that to access the Carebot container shell. 
Then you can navigate to the `/carebot` directory (whichever directory contains the `manage.py` file) and run the command `python manage.py test <path_to_test_suite>`. 
The current path to the `tests.py` file is `chat.tests`, so an example command would be `python manage.py test chat.tests.ChatViewTests` to execute each test in the `ChatViewTests` class. 
You can also run a single test function by appending the function name to the path, such as "python manage.py test chat.tests.ChatViewTests.test_chat_view_post_request_valid_data".

### 3.4. Models.py
If you would like to create any future models that describe a particular type of data you’d like to store, you can make the modification to `models.py`. 
Each new model is a single class that can represent a new data type or behavior. Any additional model must be imported into the `admin.py` file. 
You can run `docker compose down`, `docker compose build` and `docker compose up` to restart the application if a new model is added. 
For additional documentation on the purpose of the `models.py` file and its role within the Django structure, refer to this [link](https://docs.djangoproject.com/en/5.0/topics/db/models/).

### 3.5. Forms.py
Any additional method of gathering user input can be configured using `forms.py`. 
Each input form is represented as its own Python class and must be paired with a corresponding HTML element within the page that you want the user input to be collected. 
This form then needs to be instantiated within the corresponding view of the page you are using to collect user input within `views.py`. 
For additional documentation on the purpose of the `forms.py` file and its role within the Django structure, refer to this [link](https://docs.djangoproject.com/en/5.0/topics/forms/).

### 3.6. Settings.py
Any additional databases, logging mechanisms, allowed hosts, templates and middleware that are added to the application can be placed within the `settings.py` file and applied by restarting the application. 
For additional documentation on the purpose of the `settings.py` file and its role within the Django structure, refer to this [link](https://docs.djangoproject.com/en/5.0/topics/settings/).

### 3.7. Environment Variables (.env)
Any modifications or additions to the existing environment variables, such as the updating of the API secret key, must be placed in a file named `.env` to assert them as environment variables. 
They can then be loaded into the application within the `settings.py` file.

### 3.6. Dependencies
The current list of dependencies is stored within the `requirements.txt` file and is executed on any new system to ensure each new environment has all necessary dependencies. Anytime you need to add a new dependency, you can add it to the list within the `requirements.txt` file and then rebuild the project with `docker compose build`. This will automatically install any additional dependencies that are not present in the current environment.

### 3.7. Updating the Database
The current PostgreSQL database that is connected to the Chatbot is built with the data from the `database_dump.sql` file. 
Any necessary CRUD operations to the database can be done manually in this file to update the database.

### 3.8. Frontend & Static File Modification
Any modifications to the frontend, including new features or styling adaptations can be made through the corresponding HTML file of the page you want to modify. 
Each HTML file imports the CSS styling code within the `styles.css` file in the `/chat/static` directory. 
Any changes to the styling of the application should be done in this `styles.css` file. 
If you do modify the frontend, your changes may not be applied immediately as your browser may have cached previous CSS code. 
You may need to rebuild the project using the previously mentioned docker build commands. 
If you need to make any additions to the JavaScript functionality of the project, most of the JS scripts are located in `chat.js` for the interactions with the Chatbot. 
Any additional AJAX or JS features can either be included in the corresponding JS file (`chat.js` for the Chatbot page) or the corresponding HTML file for the page you are modifying.

### 3.9. Existing Backlog
The list of all issues for the Carebot project is stored in the link below in the team’s Linear page. 
This includes all tasks completed, in review, in progress and in the backlog. 
[Carebot Linear Issues](https://linear.app/carebot/team/CAR/all)

For any other documentation questions regarding the Django application, you can refer to the following links:
- [Django Documentation](https://docs.djangoproject.com/en/5.0/)
- [Django Topics](https://docs.djangoproject.com/en/5.0/topics/)
