# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import os
import sys

from apps.invoke import _run_command
from apps.lib import containerLib, lxdLib, projectLib, routeLib, utils
from invoke import task

_logger = logging.getLogger('tasks')


try:
    from pylxd.exceptions import LXDAPIException
except (ImportError, IOError) as err:
    _logger.debug(err)


@task
def stop(c, name, project=''):
    """Stop a runbot container.

    Arguments:
        name {str} -- The runbot to stop

    Keyword Arguments:
        project {str} -- The project name (default: {''})
    """
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(name, project)
    instance = containerLib.get_instance(client, container_name)
    instance.stop()


@task
def start(c, name, project=''):
    """Start a runbot container.

    Arguments:
        name {str} -- The runbot to start

    Keyword Arguments:
        project {str} -- The project name (default: {''})
    """
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(name, project)
    instance = containerLib.get_instance(client, container_name)
    instance.start(wait=True)


@task
def restart(c, name, project=''):
    """Restart a runbot container.

    Arguments:
        name {str} -- The runbot to restart

    Keyword Arguments:
        project {str} -- The project name (default: {''})
    """
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(name, project)
    instance = containerLib.get_instance(client, container_name)
    instance.restart(wait=True)


@task
def rename(c, name, new_name, project=''):
    """Rename a instance.

    To rename a instance, the instace must be stopped.
    The rename restart the instance.

    Arguments:
        name {str} -- The runbot to rename
        new_name {[type]} -- The new runbot name

    Keyword Arguments:
        project {str} -- The project (default: {''})
    """
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(name, project)
    new_container_name = containerLib.get_container_name(new_name, project)
    instance = containerLib.get_instance(client, container_name)
    _logger.info("Stopping {}".format(name))
    try:
        instance.stop()
        instance.rename(new_container_name, wait=True)
        _logger.info("Starting {}".format(name))
        instance.start()
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


@task
def move(c, name, target_project, slug, project=''):
    """Move a runbot to a project.

    For moving runbot, the runbot must be stopped.
    Slug is required, because we don't have info of
    source route.

    Arguments:
        name {str} -- The runbot name to move
        target_project {str} -- Target Project
        slug {str} -- Url prefix

    Keyword Arguments:
        project {str} -- The source project (default: {''})
    """
    slug = utils.get_slug(name)

    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)

    project_target = projectLib.get_project(c, target_project)
    target_client = lxdLib.get_pylxd_client(c, project_target)

    container_name = containerLib.get_container_name(name, project)
    new_container_name = containerLib.get_container_name(name, project_target)

    instance = containerLib.get_instance(client, container_name)
    try:
        _logger.info("Stopping {}".format(name))
        instance.stop()
        _logger.info("Moving runbot '{}' to the project '{}'".format(
            name, target_project))
        _logger.info("Can take some time!")

        instance.migrate(target_client, wait=True, live=False)
        new_instance = containerLib.get_instance(
            target_client, container_name)
        new_instance.stop()
        new_instance.rename(new_container_name, wait=True)

        _logger.info("Removing route".format(name))
        routeLib.delete_route(c, container_name)
        _logger.info("Creating new route".format(name))
        routeLib.set_route(c, project_target, new_container_name, slug=slug)

        _logger.info("Starting {}".format(name))
        new_instance.start()
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


@task
def edit_config(c, editor=''):
    """Edit the runbot configuration file.

    Actually only search on ~/runbot.yml

    Keyword Arguments:
        editor {str} -- The editor to use to edit the file (default: {''})
    """
    if c.remote:
        _logger.error('This command can\'t be run on remote server!')
        sys.exit(1)

    editor = editor or os.environ.get('EDITOR', False) or 'vim'

    _run_command(c, [
        editor,
        '~/runbot.yml'
    ], pty=True)
