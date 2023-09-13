import os
import time
import openai
import tiktoken
from rest_framework import status
from utilities.messages import ERROR_CODES
from utilities.exception import CustomAPIException
from .constants import (AI_CHAT_SYSTEM_INSTRUCTION,
                        AIModel_COMPATIBILITY_CHOICES)
from .models import (AIModel,
                     ChatQuery)
from .serializers import (ConversationSerializer,
                          ChatResponseSerializer)

openai.api_key = os.getenv('OPENAI_API_KEY')


def moderation(content):
    """
    Function to make Open AI text content moderation request.
    :param content: Text content
    :return: Moderation result
    """
    for attempt in range(1, 5):
        try:
            return openai.Moderation.create(input=content)

        except openai.error.OpenAIError as exception:
            if isinstance(exception, (openai.error.Timeout,
                                      openai.error.APIError,
                                      openai.error.RateLimitError,
                                      openai.error.APIConnectionError,
                                      openai.error.ServiceUnavailableError)) and attempt < 4:
                time.sleep(attempt * 3)
                continue
            raise CustomAPIException(
                status_code=exception.http_status,
                error_code=exception.code if exception.code else type(exception).__name__,
                error_detail=exception.user_message
            )


def get_formatted_prompt(current_conversation, chat_history, ai_model_instance):
    """
    Function to format request prompt based on model compatibility.
    :param current_conversation: Current query
    :param chat_history: Conversation history of the Chat Session
    :param ai_model_instance: Instance of requested AI Model
    :return: Formatted prompt
    :return: Maximum response tokens
    """
    max_prompt_tokens = int(0.75 * ai_model_instance.max_tokens)
    encoding = tiktoken.encoding_for_model(ai_model_instance.model_id)

    if ai_model_instance.compatibility == AIModel_COMPATIBILITY_CHOICES[0][0]:
        prompt = [f'-s> {AI_CHAT_SYSTEM_INSTRUCTION}\n',
                  f'-u> {current_conversation["content"]}\n-a> ']
        tokens_count = sum([len(encoding.encode(message)) for message in prompt])
    else:
        prompt = [{'role': 'system', 'content': AI_CHAT_SYSTEM_INSTRUCTION},
                  {'role': 'user', 'content': current_conversation['content']}]
        tokens_count = sum([len(encoding.encode(f'role:{message["role"]}\ncontent:{message["content"]}\n'))
                            for message in prompt])

    if ai_model_instance.max_tokens - tokens_count < 1:
        raise CustomAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code='token_limit_exceeded',
            error_detail=ERROR_CODES['token_limit_exceeded']
        )

    for conversation in chat_history:
        if ai_model_instance.compatibility == AIModel_COMPATIBILITY_CHOICES[0][0]:
            messages = [f'-u> {conversation["content"]}\n',
                        f'-a> {conversation["chat_responses"][-1]["content"]}\n']
            conversation_tokens_count = sum([len(encoding.encode(message)) for message in messages])
        else:
            messages = [{'role': 'user', 'content': conversation['content']},
                        {'role': 'assistant', 'content': conversation['chat_responses'][-1]['content']}]
            conversation_tokens_count = sum([len(encoding.encode(
                f'role:{message["role"]}\ncontent:{message["content"]}\n')) for message in messages])

        if (tokens_count + conversation_tokens_count) <= max_prompt_tokens:
            tokens_count += conversation_tokens_count
            prompt.insert(1, messages[0])
            prompt.insert(2, messages[1])
        else:
            break

    return prompt, ai_model_instance.max_tokens - tokens_count


def completion(model_id, chat_session_instance, query_content, regenerate=None):
    """
    Function to make Open AI chat completion API request and save the conversation.
    :param model_id: Open AI model ID
    :param chat_session_instance: Instance of the Chat Session
    :param query_content: Current query string
    :param regenerate: Chat Query instance ID for which response is to regenerated
    :return: Streaming chunks of Open AI model response
    """
    ai_model_instance = AIModel.objects.get(model_id=model_id)

    if regenerate:
        chat_history = ConversationSerializer(ChatQuery.objects.filter(
            chat_session=chat_session_instance, id__lte=regenerate
        ).order_by('-created_at')[:6], many=True).data

        current_conversation = chat_history.pop(0)

    else:
        chat_history = ConversationSerializer(ChatQuery.objects.filter(
            chat_session=chat_session_instance
        ).order_by('-created_at')[:5], many=True).data

        chat_query_serialized = ConversationSerializer(data={
            'content': query_content,
            'chat_session': chat_session_instance.id
        })
        chat_query_serialized.is_valid(raise_exception=True)
        chat_query_serialized.save()
        current_conversation = chat_query_serialized.data

    regenerations_count = int(str(len(current_conversation['chat_responses']))[-1])
    prompt, max_response_tokens = get_formatted_prompt(current_conversation=current_conversation,
                                                       chat_history=chat_history,
                                                       ai_model_instance=ai_model_instance)

    chat_response_data = {
        'content': str(),
        'chat_query': current_conversation['id']
    }
    for attempt in range(1, 5):
        try:
            if ai_model_instance.compatibility == AIModel_COMPATIBILITY_CHOICES[0][0]:
                for chunk in openai.Completion.create(
                    stream=True,
                    model=ai_model_instance.model_id,
                    prompt=''.join(prompt),
                    max_tokens=int(max_response_tokens),
                    temperature=round(1.6 - 0.08 * regenerations_count, 2) if regenerations_count else 0.8
                ):
                    chunk_content = chunk['choices'][0]['text']
                    chat_response_data['content'] += chunk_content
                    yield chunk_content

            else:
                for chunk in openai.ChatCompletion.create(
                    stream=True,
                    model=ai_model_instance.model_id,
                    messages=prompt,
                    max_tokens=int(max_response_tokens),
                    temperature=round(1.2 - 0.04 * regenerations_count, 2) if regenerations_count else 0.8
                ):
                    chunk_content = chunk['choices'][0]['delta'].get('content')
                    if chunk_content:
                        chat_response_data['content'] += chunk_content
                        yield chunk_content

            break

        except openai.error.OpenAIError as exception:
            if isinstance(exception, (openai.error.Timeout,
                                      openai.error.APIError,
                                      openai.error.RateLimitError,
                                      openai.error.APIConnectionError,
                                      openai.error.ServiceUnavailableError)) and attempt < 4:
                time.sleep(attempt * 3)
                continue
            raise CustomAPIException(
                status_code=exception.http_status,
                error_code=exception.code if exception.code else type(exception).__name__,
                error_detail=exception.user_message
            )

    chat_response_serialized = ChatResponseSerializer(data=chat_response_data)
    chat_response_serialized.is_valid(raise_exception=True)
    chat_response_serialized.save()
