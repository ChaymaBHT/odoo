# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import os
import shelve
import sys

_logger = logging.getLogger('tasks')

try:
    from pylxd.exceptions import LXDAPIException
except (ImportError, IOError) as err:
    _logger.debug(err)


def check_project(client, project):
    """Check if the projec exists.

    Arguments:
        client {Client} -- LXD Client
        project {str} -- Name of the project to check
    """
    if not project:
        return

    try:
        project = client.projects.get(project)
    except LXDAPIException:
        _logger.error("Project {} doesn't exists!".format(project))
        sys.exit(1)


def get_project(c, project):
    """Return the project or the default project.

    If the project is empty, return the default project
    define on the config with the param "default_project".

    Arguments:
        project {str} -- Project Name

    Returns:
        str -- The project name to use
    """
    if project:
        return project

    user_default_project = get_user_default_project(c)
    if user_default_project:
        return user_default_project

    return c.default_project


def get_project_config(c, project):
    """Return the config data of a project.

    Use the param projects of the config file.

    Arguments:
        project {str} -- Project name to have the config.

    Returns:
        [type] -- [description]
    """
    if project in c.projects:
        return c.projects[project]

    return {
        'url': '',
        'description': '',
        'default_app': '',
    }


def set_user_default_project(c, project):
    file_path = os.path.expanduser('~/.runbot.cfg')
    shelf = shelve.open(file_path)
    shelf['default_project'] = project
    shelf.close()


def get_user_default_project(c):
    file_path = os.path.expanduser('~/.runbot.cfg')
    shelf = shelve.open(file_path)
    default_project = shelf.get('default_project')
    shelf.close()
    return default_project
