from datetime import datetime
from logging import NullHandler, getLogger


DATESTAMP_TEMPLATE = '%Y%m%d'
TIMESTAMP_TEMPLATE = DATESTAMP_TEMPLATE + '-%H%M'


def get_log(name):
    log = getLogger(name)
    log.addHandler(NullHandler())
    return log


def get_timestamp(when=None, template=TIMESTAMP_TEMPLATE):
    if when is None:
        # Use local time
        when = datetime.now()
    return when.strftime(template)
