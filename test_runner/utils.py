import logging
import sys
import uuid

from contextlib import contextmanager
from subprocess import check_call, CalledProcessError

LOG = logging.getLogger(__name__)


class Reporter(object):

    def __init__(self, name):
        self.name = name

    def setup(self):
        logger = logging.getLogger('test_runner')

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)

        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)
        ch.setFormatter(formatter)

        logger.setLevel(logging.DEBUG)
        logger.addHandler(ch)

        return logger


def run_cmd(command):
    """ Runs a command and returns an array of its results

    :param command: String of a command to run within a shell
    :returns: Dictionary with keys relating to the execution's success
    """
    try:
        ret = check_call(command, shell=True)
        return {'success': True, 'return': ret, 'exception': None}
    except CalledProcessError as exc:
        return {'success': False,
                'return': None,
                'exception': exc,
                'command': command}

@contextmanager
def cleanup(stage):
    try:
        yield
    except (Exception, KeyboardInterrupt):
        LOG.exception('Run failed')
    finally:
        stage.destroy()


def rand_name(prefix):
     return '{}-{}'.format(prefix, str(uuid.uuid4()))
