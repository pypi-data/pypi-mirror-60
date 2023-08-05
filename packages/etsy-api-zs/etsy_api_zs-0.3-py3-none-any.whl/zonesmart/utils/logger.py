import logging
import os

from django.conf import settings


def get_logger(app_name=None, filename=None, file=True, console=True):
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")

    if file:
        # Get path
        path = os.path.join(
            settings.LOG_DIR, os.path.splitext(os.path.basename(app_name))[0] + ".log",
        )
        # Create file if not exists
        if not os.path.exists(path):
            f = open(path, "w+")
            f.close()
        # Set logger
        fh = logging.FileHandler(path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


# class Logger:
#     def __init__(self, app_name):
#         self.app_name = app_name
#
#     def info(self, message):
#         if settings.DEBUG:
#             logger = get_logger(self.app_name)
#             logger.info(message)
#         else:
#             from sentry_sdk import capture_message
#
#             capture_message(f"{self.app_name} | {message}")
