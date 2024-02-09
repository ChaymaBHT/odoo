# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import sys
from getpass import getpass

import urllib3
from apps.collections.apiTasks import _get_key_file_prefix
from apps.lib import projectLib

_logger = logging.getLogger('tasks')

try:
    from pylxd import Client
    from pylxd.exceptions import ClientConnectionFailed, LXDAPIException
except (ImportError, IOError) as err:
    _logger.debug(err)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_pylxd_client(c, project=''):
    """Return the pylxd client.

    If not remote use the lxd socket.
    if remote and not authenticates, ask the password for authentification.

    After init the client, check if the project exists.

    Keyword Arguments:
        project {str} -- A LXD project (default: {''})

    Returns:
        Client -- The pylxd client
    """
    if not c.remote:
        try:
            return Client(
                project=project
            )
        except ClientConnectionFailed as e:
            _logger.error(str(e))
            sys.exit(1)
        except LXDAPIException as e:
            _logger.error(str(e))
            sys.exit(1)

    _check_remote_config(c)

    key_prefix = _get_key_file_prefix(c)
    cert = ('{}.crt'.format(key_prefix), '{}.key'.format(key_prefix))
    client = False
    try:
        client = Client(
            endpoint=c.remote_endpoint,
            cert=(cert),
            verify=False,
            project=project
        )

        if not client.trusted:
            pswd = getpass('Endpoint Password:')
            client.authenticate(pswd)
    except ClientConnectionFailed as e:
        _logger.error(str(e))
        sys.exit(1)
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)

    projectLib.check_project(client, project)
    if project:
        _logger.info("Using project '{}'".format(project))

    return client


def _check_remote_config(c):
    if not c.remote_endpoint:
        _logger.error('You should specify an url for the endpoint')
        _logger.error('ex: https://1.2.3.4:8443')
        sys.exit(1)
