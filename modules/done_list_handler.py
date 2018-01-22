from modules import config

from enum import Enum, auto


class Status(Enum):
    SUCCESS = auto()
    FAIL = auto()
    UNDEFINED = auto()


class DoneListHandler:
    def __init__(self):
        self.done_list = open(config.DONE_LIST, 'a+')

    def write(self, app_name, status, reason=None, comment=None):
        if not config.IGNORE_DONE_LIST:
            str = f'{app_name}: {status.name}'
            if status in [Status.FAIL, Status.UNDEFINED]:
                str += f', REASON: {reason}'
            if comment is not None:
                str += f', COMMENT: {comment}'
            self.done_list.write(str+'\n')
            self.done_list.flush()

    def get_done_project_names(self):
        self.done_list.seek(0)
        done_project_names = [line.split(': ')[0] for line in self.done_list.readlines() if 'UNDEFINED' not in line]
        return done_project_names

    def get_fail_counter(self):
        self.done_list.seek(0)
        fail_counter = self.done_list.read().count('FAIL')
        return fail_counter

    def close(self):
        self.done_list.close()


list_handler = DoneListHandler()
