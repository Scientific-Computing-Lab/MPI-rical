import os
import logging as log


def set_logger(log_path=None, format='[%(asctime)s %(levelname)s] %(message)s', filemode='a'):
    log.root.handlers = []
    handlers = [log.StreamHandler()]
    if log_path:
        d = os.path.split(log_path)[0]
        if not os.path.isdir(d):
            os.makedirs(d)
        handlers.append(log.FileHandler(log_path, mode=filemode))
    log.basicConfig(level=log.INFO,
                    format=format,
                    handlers=handlers)
    return log


info = log.info
warning = log.warning
error = log.error
