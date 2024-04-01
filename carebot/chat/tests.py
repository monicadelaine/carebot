from django.test import TestCase, Client
from django.urls import reverse
from .models import Message, MessageType
import logging
from unittest.mock import patch, MagicMock


class ChatViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.chat_url = reverse('chat')

    def test_chat_view_get_request(self):
        #Tests the GET request
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat.html')

    def test_chat_view_post_request_valid_data(self):
        #Tests the POST request with valid data
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

