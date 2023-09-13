from django.urls import path

from .views import (GetAIModels,
                    GetChatSessions,
                    GetConversations,
                    ContentModeration,
                    CreateChatSession,
                    CreateConversation)


urlpatterns = [
    path('getAIModels', GetAIModels.as_view(), name='get-ai-models'),
    path('createChatSession', CreateChatSession.as_view(), name='create-chat-session'),
    path('getChatSessions', GetChatSessions.as_view(), name='get-chat-sessions'),
    path('createConversation/<int:pk>', CreateConversation.as_view(), name='create-conversation'),
    path('getConversations/<int:pk>', GetConversations.as_view(), name='get-conversations'),
    path('contentModeration', ContentModeration.as_view(), name='content-moderation'),
]
