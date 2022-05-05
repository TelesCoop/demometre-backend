from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code and the message code to the response.
    if response is not None:
        response.data["status_code"] = response.status_code
        if isinstance(response.data["detail"].code, dict):
            response.data["field"] = response.data["detail"].code["field"]
            response.data["message_code"] = response.data["detail"].code["code"]
        else:
            response.data["message_code"] = response.data["detail"].code

    return response


class ValidationFieldError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid input."
    default_code = "invalid"

    def __init__(self, field, code=None, detail=None):
        code = {"field": field, "code": code}
        super().__init__(detail, code)
