import os
import sys
import time
import subprocess
from loguru import logger
from modules import shellhelper
from modules.exceptions import AbsentActivityException, UserExitException


class Agent(object):
    def __init__(self):
        pass

    def run(self, apk):
        pass

    @staticmethod
    def read_status_from_experimenter():
        print("Press: c - crashed, s - successed, e - exit")
        key = Agent.wait_key()
        while key != 's' and key != 'c' and key != 'e':
            print("Press: c - crashed, s - successed, e - exit")
            key = Agent.wait_key()
        if key == 'e':
            raise UserExitException()
        return key

    @staticmethod
    def wait_key():
        ''' Wait for a key press on the console and return it. '''
        result = None
        if os.name == 'nt':
            import msvcrt
            result = msvcrt.getch()
        else:
            import termios
            fd = sys.stdin.fileno()
            oldterm = termios.tcgetattr(fd)
            newattr = termios.tcgetattr(fd)
            newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, newattr)
            try:
                result = sys.stdin.read(1)
            except IOError:
                pass
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        return result.decode('utf-8')

    @staticmethod
    def wait_for_boot():
        cmd = "adb shell getprop dev.bootcomplete"
        res = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
        while res != '1':
            logger.info("wait for devices")
            time.sleep(5)
            comm = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE).communicate()
            if len(comm) > 0 and comm[0] != None:
                res = comm[0].strip()


class ActivityAgent(Agent):
    def __init__(self):
        super().__init__()

    def run(self, apk):
        main_activity_name = apk.activity
        if main_activity_name is None:
            raise AbsentActivityException
        shellhelper.clean_log()
        shellhelper.start_activity_explicitly(apk.package, main_activity_name)


class MonkeyAgent(Agent):
    def __init__(self, seed, throttle, event_num):
        super().__init__()
        self.seed = seed
        self.throttle = throttle
        self.event_num = event_num

    def run(self, apk):
        shellhelper.run_monkey(apk.package, self.seed, self.throttle,
                               self.event_num)
