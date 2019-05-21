from loguru import logger

import subprocess


def log(msg_before):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            logger.info(f'{self.apk.package}: {msg_before}')
            func(self, *args, **kwargs)
        return wrapper
    return decorator



