from django.db import models

from utilities.mixins import (ModelCreatedAtMixin,
                              ModelTimeStampMixin)
from .constants import AIModel_COMPATIBILITY_CHOICES


class AIModel(models.Model):
    """
    Model for storing OpenAI model details.
    """
    model_id = models.CharField(null=False, blank=False, unique=True, max_length=100)
    max_tokens = models.IntegerField(null=False, blank=False)
    compatibility = models.CharField(null=False, blank=False, max_length=100, choices=AIModel_COMPATIBILITY_CHOICES)

    class Meta:
        verbose_name = 'AI Model'


class ChatSession(ModelTimeStampMixin):
    """
    Model for managing chat sessions.
    """
    title = models.CharField(null=False, blank=False, unique=True, max_length=200)


class ChatQuery(ModelCreatedAtMixin):
    """
    Model for user chat queries.
    """
    content = models.TextField(null=False, blank=False)
    chat_session = models.ForeignKey(ChatSession, null=False, blank=False,
                                     related_name='r_chat_queries', on_delete=models.CASCADE)


class ChatResponse(ModelCreatedAtMixin):
    """
    Model for LLM responses.
    """
    content = models.TextField(null=False, blank=False)
    chat_query = models.ForeignKey(ChatQuery, null=False, blank=False,
                                   related_name='r_chat_responses', on_delete=models.CASCADE)
