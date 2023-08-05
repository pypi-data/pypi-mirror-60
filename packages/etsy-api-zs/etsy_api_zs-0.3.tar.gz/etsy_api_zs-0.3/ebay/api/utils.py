import logging


def disable_logger(logger, new_level=logging.CRITICAL):
    def _disable_logger(method):
        def wrapper(self, **kwargs):
            silent = getattr(self, "silent", False)
            if silent:
                old_level = logger.level
                logger.level = new_level
            result = method(self, **kwargs)
            if silent:
                logger.level = old_level
            return result

        return wrapper

    return _disable_logger
