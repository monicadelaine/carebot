from django.db import models

class Message(models.Model):
    # Used to store messages sent by the user and the chatbot
    from_user = models.BooleanField()   # True if the message is from the user, False if it is from the chatbot
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text