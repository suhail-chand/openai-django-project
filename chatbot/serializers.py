from rest_framework.serializers import ModelSerializer

from .models import (AIModel,
                     ChatQuery,
                     ChatSession,
                     ChatResponse)


class AIModelSerializer(ModelSerializer):
    class Meta:
        model = AIModel
        fields = '__all__'


class ChatSessionSerializer(ModelSerializer):
    class Meta:
        model = ChatSession
        fields = '__all__'


class ChatResponseSerializer(ModelSerializer):
    class Meta:
        model = ChatResponse
        fields = '__all__'


class ConversationSerializer(ModelSerializer):
    chat_responses = ChatResponseSerializer(source='r_chat_responses', many=True, read_only=True)

    class Meta:
        model = ChatQuery
        fields = '__all__'
