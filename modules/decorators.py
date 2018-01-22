import logging

import subprocess


def log(msg_before):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            logging.info(f'{self.apk.package}: {msg_before}')
            func(self, *args, **kwargs)
        return wrapper
    return decorator



