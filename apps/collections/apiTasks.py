# Copyright 2022      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import os
import sys

from apps.invoke import _run_command
from apps.lib import lxdLib
from invoke import Collection, task

_logger = logging.getLogger('tasks')

apiCollection = Collection('api')


@task
def generate_keys(c):
    """Generate keys for remotes access.

    The runbot tools can use the lxd api to access a remote
    LXD server.

    The keys are used to encrypt the connection on the client
    and the server.

    By default, the key is not required and used the local socket
    LXD.

    To configure the remote add this entry on the configuration file:
    * "remote" to True, by default is False
    * "remote_endpoint", the remote url and port to access the server.
    """
    key_file_prefix = _get_key_file_prefix(c)

    if os.path.exists("{}.key".format(key_file_prefix)):
        _logger.error('The key file for the runbot already exists!')
        _logger.error("{}.key".format(key_file_prefix))
        sys.exit(1)

    command = [
        'openssl req -newkey rsa:2048 -nodes',
        '-keyout {}.key'.format(key_file_prefix),
        '-out {}.csr'.format(key_file_prefix),
    ]
    _run_command(c, command)

    command = [
        'openssl x509',
        '-signkey {}.key'.format(key_file_prefix),
        '-in {}.csr'.format(key_file_prefix),
        '-req -days 365 -out {}.crt'.format(key_file_prefix)
    ]
    _run_command(c, command)


@task
def authenticate(c):
    """Authenticate the remote access.

    If you are not authentificate, when a command is
    launch, a password request will be prompt.
    """
    if not c.remote:
        _logger.error("Authenticate is only required for a remote access.")
        sys.exit(1)

    client = lxdLib.get_pylxd_client(c)
    if client.trusted:
        _logger.info("Remote already authenticate.")


@task
def check_keys(c):
    """Check keys for remotes access.

    Check if the key can be found on the client.
    """
    key_file_prefix = _get_key_file_prefix(c)

    if not os.path.exists("{}.key".format(key_file_prefix)):
        _logger.error('The key file for the runbot not exists!')
        _logger.error("{}.key".format(key_file_prefix))
        sys.exit(1)

    if not os.path.exists("{}.crt".format(key_file_prefix)):
        _logger.error('The crt file for the runbot not exists!')
        _logger.error("{}.crt".format(key_file_prefix))
        sys.exit(1)

    if not os.path.exists("{}.csr".format(key_file_prefix)):
        _logger.error('The csr file for the runbot not exists!')
        _logger.error("{}.csr".format(key_file_prefix))
        sys.exit(1)

    _logger.info('The keys is correctly installed on {}.*'.format(
        key_file_prefix))


def _get_key_file_prefix(c):
    key_folder = c.local_keys_folder
    key_prefix = c.local_key_prefix

    key_folder = os.path.expanduser(key_folder)
    return '{}/{}'.format(key_folder, key_prefix)


apiCollection.add_task(generate_keys)
apiCollection.add_task(check_keys)
apiCollection.add_task(authenticate)
