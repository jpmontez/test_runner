import logging
import os
import uuid

from contextlib import contextmanager
from subprocess import check_call, CalledProcessError

LOG = logging.getLogger(__name__)


def touch(directory, filename=None):
    file_path = os.path.join(directory, filename)

    if os.path.exists(file_path):
        os.utime(file_path, None)
    else:
        os.makedirs(directory)

    if filename is not None:
        open(file_path, 'a').close()

    return file_path


def run_cmd(command, **kwargs):
    """ Runs a command and returns an array of its results

    :param command: String of a command to run within a shell
    :returns: Dictionary with keys relating to the execution's success
    """
    cwd = kwargs.get('cwd', None)

    try:
        ret = check_call(command, shell=True, cwd=cwd)
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
