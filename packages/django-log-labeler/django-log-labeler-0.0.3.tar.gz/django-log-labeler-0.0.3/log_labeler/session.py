from requests import Session as BaseSession
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from log_request_id import local, LOG_LABEL_REQUEST_SETTING, DEFAULT_HEADER_VALUE, LOG_LABEL_LOGGER_NAME


class Session(BaseSession):
    def __init__(self, *args, **kwargs):
        log_label_request_settings = getattr(settings, LOG_LABEL_REQUEST_SETTING, False)
        if log_label_request_settings:
            for label, header_name in log_label_request_settings.items():
                setattr(self, label, header_name)
        else:
            raise ImproperlyConfigured("The %s settings must be configured in "
                "order to use %s" % (
                   LOG_LABEL_REQUEST_SETTING,
                   __name__
            ))
        super(Session, self).__init__(*args, **kwargs)

    def prepare_request(self, request):
        """Include the request ID, if available, in the outgoing request"""
        log_label_request_settings = getattr(settings, LOG_LABEL_REQUEST_SETTING, False)

        if log_label_request_settings:
            for label, header_name in log_label_request_settings.items():
                header_value = getattr(local, header_name, False)
                if header_value:
                    request.headers[local] = getattr(local, header_name, False)

        return super(Session, self).prepare_request(request)
