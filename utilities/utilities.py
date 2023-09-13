import json
from rest_framework.renderers import BaseRenderer
from rest_framework.pagination import CursorPagination


class CustomResponseRenderer(BaseRenderer):
    """
    Response renderer class to format response data.
    """
    format = 'txt'
    media_type = 'application/json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if type(data) is dict:
            response = {
                'status_code': renderer_context['response'].status_code,
                'data': data.get('data', None),
                'error': data.get('error', None),
                'message': data.get('message',
                                    'SUCCESS'
                                    if renderer_context['response'].status_code in range(200, 300)
                                    else 'FAILURE'),
            }
        else:
            response = {
                'status_code': renderer_context['response'].status_code,
                'data': data,
                'error': None,
                'message':
                    'SUCCESS' if renderer_context['response'].status_code in range(200, 300) else 'FAILURE',
            }

        return json.dumps(response)


class CustomCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'

    def get_paginated_response(self, data):
        return {
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'results': data
            }
