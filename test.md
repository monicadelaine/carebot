### Testing the Chatbot Application

For any additional unit tests needed for the application, you can create the necessary classes and functions for each new unit test.
The general structure allows you to create a class for a particular file or function of the application, where each class contains a collection of functions to test a certain feature.
You can either add functions to one or multiple classes or create a new class to test a separate function of the application.
For additional documentation on the purpose of the `tests.py` file and its role within the Django structure, refer to this [link](https://docs.djangoproject.com/en/5.0/topics/testing/).

#### Running Unit Tests

To test the application with a particular test suite, you must navigate to the docker container of the application.
While the application is running, you can either open a new terminal and run the commands `docker ps` (to list each current docker process running) and `docker exec -it <docker_container_id> /bin/bash` to create a shell within the Carebot docker container.
Make sure to use the container ID for the Carebot container rather than the database container.
If you are using Docker Desktop, you can simply use that to access the Carebot container shell.
Then you can navigate to the `/carebot` directory (whichever directory contains the `manage.py` file) and run the command `python manage.py test <path_to_test_suite>`.
The current path to the `tests.py` file is `chat.tests`, so an example command would be `python manage.py test chat.tests.ChatViewTests` to execute each test in the `ChatViewTests` class.
You can also run a single test function by appending the function name to the path, such as "python manage.py test chat.tests.ChatViewTests.test_chat_view_post_request_valid_data".

## Complete List of Unit Tests
#### ChatViewTests

- **setUp(self):**
  - Initializes the client and chat URL.
  
- **test_chat_view_get_request:**
  - Tests the GET request.
  - Verifies the status code and template used.

- **test_chat_view_post_request_valid_data:**
  - Tests the POST request with valid data.
  - Verifies the status code and presence of 'response' in JSON.

- **test_chat_view_post_request_invalid_data:**
  - Tests handling of POST requests with invalid data.
  - Verifies the status code and presence of 'error' in JSON.

#### MessageModelTests

- **test_message_creation:**
  - Tests message creation.
  - Verifies the creation of a message instance and its string representation.

#### AJAXChatViewTests

- **setUp(self):**
  - Sets up an AJAX request with required headers.

- **test_ajax_post_request_valid_data:**
  - Tests AJAX POST request with valid data.
  - Verifies the status code and presence of 'response' in JSON.

- **test_ajax_post_request_invalid_data:**
  - Tests AJAX POST request with invalid data.
  - Verifies the status code and presence of 'error' in JSON.

#### SessionManagementTests

- **test_clear_session:**
  - Tests clearing of session.
  - Verifies the status code and response indicating session clearance.

#### DatabaseInteractionTests

- **test_message_storage:**
  - Tests message storage in the database.
  - Verifies the count of stored messages and their attributes.
 
- **ChatViewTests:**
  ```python
  class ChatViewTests(TestCase):
      def setUp(self):
          self.client = Client()
          self.chat_url = reverse('chat')

      def test_chat_view_get_request(self):
          # Tests the GET request
          response = self.client.get(self.chat_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'chat/chat.html')

      def test_chat_view_post_request_valid_data(self):
          # Tests the POST request with valid data
          response = self.client.post(self.chat_url, {'query': 'Hello, chatbot!'})
          self.assertEqual(response.status_code, 200)
          self.assertIn('response', response.json())

      def test_chat_view_post_request_invalid_data(self):
          # Test handling of POST requests with invalid data
          response = self.client.post(self.chat_url, {})
          self.assertEqual(response.status_code, 400)
          self.assertIn('error', response.json())

class MessageModelTests(TestCase):
    def test_message_creation(self):
        # Test message creation
        message = Message.objects.create(message_type=MessageType.USER, text="Test message")
        self.assertTrue(isinstance(message, Message))
        self.assertEqual(message.__str__(), "Test message")

class AJAXChatViewTests(TestCase):
    def setUp(self):
        # Mimic an AJAX request
        self.client = Client()
        self.chat_url = reverse('chat')
        self.headers = {
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
        }

    def test_ajax_post_request_valid_data(self):
        response = self.client.post(self.chat_url, {'query': 'Hello, chatbot!'}, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())

    def test_ajax_post_request_invalid_data(self):
        response = self.client.post(self.chat_url, {}, **self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

class SessionManagementTests(TestCase):
    def test_clear_session(self):
        session_clear_url = reverse('clear_session')
        response = self.client.post(session_clear_url, {}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'session_cleared'})

class DatabaseInteractionTests(TestCase):
    def test_message_storage(self):
        chat_url = reverse('chat')
        self.client.post(chat_url, {'query': 'Test message'}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        self.assertEqual(Message.objects.count(), 2)
        message = Message.objects.first()
        self.assertEqual(message.text, 'Test message')
        self.assertEqual(message.message_type, MessageType.USER)
        ```


