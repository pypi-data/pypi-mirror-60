import logging
from django.conf import settings
from log_labeler import local, DEFAULT_HEADER_VALUE, LOG_LABEL_REQUEST_SETTING


class HeaderToLabelFilter(logging.Filter):
    def filter(self, record):
        if hasattr(settings, LOG_LABEL_REQUEST_SETTING) and isinstance(getattr(settings, LOG_LABEL_REQUEST_SETTING), dict):
            for label, header_name in getattr(settings, LOG_LABEL_REQUEST_SETTING).items():
                setattr(record, label, getattr(local, header_name, DEFAULT_HEADER_VALUE))
        return True
