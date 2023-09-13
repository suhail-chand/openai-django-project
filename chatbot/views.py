from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from rest_framework.generics import (ListAPIView,
                                     CreateAPIView)

from utilities import messages
from utilities.utilities import CustomCursorPagination

from .models import (AIModel,
                     ChatQuery,
                     ChatSession)
from .open_ai import completion, moderation
from .serializers import (AIModelSerializer,
                          ChatSessionSerializer,
                          ConversationSerializer)


class GetAIModels(ListAPIView):
    """
    API to get a list of all AIModel instances.
    """
    serializer_class = AIModelSerializer

    def get_queryset(self):
        return AIModel.objects.all()

    def list(self, request, *args, **kwargs):
        return Response({"data": self.get_serializer(self.get_queryset(), many=True).data,
                         "message": messages.FETCHED.format('AI models')},
                        status=status.HTTP_200_OK)


class CreateChatSession(CreateAPIView):
    """
    API to start a chat session.
    """
    serializer_class = ChatSessionSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        chat_session_serialized = self.get_serializer(data={'title': request.data['title']})
        chat_session_serialized.is_valid(raise_exception=True)

        return StreamingHttpResponse(
            completion(
                model_id=request.data["model_id"],
                chat_session_instance=chat_session_serialized.save(),
                query_content=request.data['query_content']),
            content_type='text/event-stream')


class GetChatSessions(ListAPIView):
    """
    API to fetch chat sessions.
    """
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.all()

    def list(self, request, *args, **kwargs):
        return Response({'data': {'chat_sessions': super().list(request, *args, **kwargs).data},
                         'message': messages.FETCHED.format('Chat sessions')},
                        status=status.HTTP_200_OK)


class CreateConversation(CreateAPIView):
    """
    API to converse in a chat session.
    """
    serializer_class = ConversationSerializer

    def get_object(self):
        return ChatSession.objects.get(id=self.kwargs['pk'])

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return StreamingHttpResponse(
            completion(
                model_id=request.data["model_id"],
                chat_session_instance=self.get_object(),
                query_content=request.data.get('query_content'),
                regenerate=int(request.GET.get('regenerate'))
                if str(request.GET.get('regenerate')).isdigit() else None
            ),
            content_type='text/event-stream')


class GetConversations(ListAPIView):
    """
    API to fetch conversations of a chat session.
    """
    serializer_class = ConversationSerializer
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        return ChatQuery.objects.filter(chat_session=ChatSession.objects.get(id=self.kwargs['pk']))

    def list(self, request, *args, **kwargs):
        return Response({'data': super().list(request, *args, **kwargs),
                         'message': messages.FETCHED.format('Conversations')},
                        status=status.HTTP_200_OK)


class ContentModeration(CreateAPIView):
    """
    API to generate text content moderation results.
    """

    def post(self, request, *args, **kwargs):
        return Response({'data': moderation(request.data['content']),
                         'message': messages.FETCHED.format('Moderation results')},
                        status=status.HTTP_200_OK)
