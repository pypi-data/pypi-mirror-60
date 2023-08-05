import logging
import uuid

from django.conf import settings
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object
from log_labeler import local, LOG_LABEL_REQUEST_SETTING, DEFAULT_HEADER_VALUE, LOG_LABEL_LOGGER_NAME


if hasattr(settings, LOG_LABEL_LOGGER_NAME, False):
    logger = logging.getLogger(getattr(settings, LOG_LABEL_LOGGER_NAME))
else:
    logger = logging.getLogger(__name__)


class HeaderToLabelMiddleware(MiddlewareMixin):
    def process_request(self, request):
        log_label_request_settings = getattr(settings, LOG_LABEL_REQUEST_SETTING, False)
        if log_label_request_settings:
            for label, header_name in log_label_request_settings.items():
                header_value = self._get_header(request, header_name)
                setattr(local, label, header_value)
                setattr(request, label, header_value)


    def process_response(self, request, response):
        log_label_request_settings = getattr(settings, LOG_LABEL_REQUEST_SETTING, False)

        if log_label_request_settings:
            for label in log_label_request_settings:
                response[label] = getattr(request, label)

        return response

    def _get_header(self, request, header_name):
        return request.META.get(header_name, DEFAULT_HEADER_VALUE)
