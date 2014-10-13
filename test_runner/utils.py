import logging
import sys
import uuid

from contextlib import contextmanager
from subprocess import check_call, CalledProcessError

LOG = logging.getLogger(__name__)


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
