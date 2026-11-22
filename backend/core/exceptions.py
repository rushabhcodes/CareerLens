import logging
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": {
                "message": " ".join(str(x) for x in response.data.get("detail", []))
                if isinstance(response.data.get("detail"), list)
                else str(
                    response.data.get("detail", "Please check the highlighted fields.")
                ),
                "fields": response.data,
            }
        }
    elif isinstance(exc, DatabaseError):
        logger.exception("Database request failed")
        return Response(
            {
                "error": {
                    "message": "The database is temporarily unavailable. Please try again."
                }
            },
            status=503,
        )
    return response
