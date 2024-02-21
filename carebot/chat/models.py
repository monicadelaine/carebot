from django.db import models
from enum import IntEnum

class MessageType(IntEnum):
    USER = 0
    CHATBOT = 1
    SYSTEM = 2

class Message(models.Model):
    # Used to store messages sent by the user and the chatbot
    message_type = models.IntegerField(choices=[(tag, tag.name) for tag in MessageType], default=MessageType.USER)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
