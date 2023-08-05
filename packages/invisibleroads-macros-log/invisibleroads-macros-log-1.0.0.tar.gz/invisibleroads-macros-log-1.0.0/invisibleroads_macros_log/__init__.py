from logging import NullHandler, getLogger


def get_log(name):
    log = getLogger(name)
    log.addHandler(NullHandler())
    return log
