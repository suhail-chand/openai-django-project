import re
import logging
import traceback
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import (ErrorDetail,
                                       APIException)
from rest_framework.views import (set_rollback,
                                  exception_handler)
from django.core.exceptions import (ValidationError,
                                    ObjectDoesNotExist)

from utilities import messages


def traverse_exception_handler_response_data(data, error_detail_list):
    """
    Function to traverse through rest-framework's exception-handler's
    response data and return a list of ErrorDetail instances.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            error_detail_list = traverse_exception_handler_response_data(value, error_detail_list)
    elif isinstance(data, list):
        for item in data:
            error_detail_list = traverse_exception_handler_response_data(item, error_detail_list)
    elif isinstance(data, ErrorDetail):
        error_detail_list.append(data)

    return error_detail_list


def custom_exception_handler(exception, context):
    """
    Function to handle exceptions.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    response_data = {
        'error': list(),
        'message': list()
    }

    if isinstance(exception, ValidationError):
        response_data['error'] = [error.code for error in exception.error_list]
        response_data['message'] = [error.message for error in exception.error_list]

    elif isinstance(exception, ObjectDoesNotExist):
        status_code = status.HTTP_404_NOT_FOUND
        response_data['error'].append(type(exception).__name__)
        response_data['message'].append(messages.DOES_NOT_EXIST.format(
            re.sub(r'(\w)([A-Z])', r'\1 \2', str(exception).split()[0].replace('Custom', ''))))

    else:
        # Call REST framework's default exception handler to get the standard error response.
        exception_handler_response = exception_handler(exception, context)

        if exception_handler_response:
            status_code = exception_handler_response.status_code
            for error_detail in traverse_exception_handler_response_data(
                    exception_handler_response.data, list()):
                response_data['error'].append(error_detail.code)
                response_data['message'].append(str(error_detail))

            response_data['error'] = list(set(response_data['error']))
            response_data['message'] = response_data['message'][-1:-(len(response_data['error'])+1):-1]

    # Rollback unused DB calls.
    set_rollback()

    if response_data['error'] or response_data['message']:
        return Response(response_data, status=status_code)

    else:
        logging.getLogger('django').exception(exception, exc_info=True)
        return Response({
            'error': {
                'type': type(exception).__name__,
                'value': str(exception),
                'traceback': traceback.format_exc().splitlines()[1:-1]
            },
            'message': messages.UNKNOWN_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomAPIException(APIException):
    def __init__(self, status_code, error_code, error_detail):
        self.status_code = status_code
        self.default_code = error_code
        self.default_detail = error_detail
        super().__init__(self.default_detail, self.default_code)
