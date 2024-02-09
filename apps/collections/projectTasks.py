# Copyright 2022      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import sys

from apps.lib import lxdLib, projectLib
from invoke import Collection, task
from tabulate import tabulate

_logger = logging.getLogger('tasks')

try:
    from pylxd.exceptions import LXDAPIException
except (ImportError, IOError) as err:
    _logger.debug(err)

projectCollection = Collection('project')


@task
def init_default(c):
    """Init default projects.

    Projects description:

    * default: for system container like reverse proxy.
    * runbots: Default project to store runbot instances.
    * demo: Project to store demo instances.
    """

    client = lxdLib.get_pylxd_client(c)

    for project in c.projects:
        description = c.projects.get(project).get('description', '')
        try:
            lxd_project = client.projects.get(project)
            if not lxd_project.description:
                update(c, project, description)
            _logger.info('Project {} already exists'.format(project))
        except LXDAPIException:
            create(c, project, description)

    update(c, 'default', 'Project for system containers like reverse proxy.')


@task
def list(c, all=False):
    """List all runbots project.

    Runbot project can be represented by a gitlab project.
    All instance created to this project is only visible for
    the project.
    """
    client = lxdLib.get_pylxd_client(c)
    projects = []
    lxd_projects = []
    try:
        lxd_projects = client.projects.all()
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)

    for project in lxd_projects:
        project_c = projectLib.get_project_config(c, project.name)
        if not all and project_c.get('disabled', False):
            continue

        if not all and project.name == 'default':
            continue

        projects.append([
            project.name,
            project_c['url'],
            project.description,
        ])

    print(tabulate(projects, headers=[
        "Name",
        "Url Suffix",
        "Description",
    ], tablefmt="orgtbl"))


@task
def create(c, name, description):
    """Create a new project.

    Create a new project, the project created share
    the network and images with other projects.

    Arguments:
        name {str} -- Name of the new project
        description {str} -- Description of the new project
    """
    client = lxdLib.get_pylxd_client(c)
    try:
        project = client.projects.create(
            name, description=description, config={
                'features.images': 'false',
                'features.profiles': 'false',
            })
        _logger.info("Project {} created".format(project.name))
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


@task
def update(c, name, description):
    """Update project description.

    Update the project description.

    Arguments:
        name {str} -- The name of project to update.
        description {str} -- New description
    """
    client = lxdLib.get_pylxd_client(c)
    try:
        lxd_project = client.projects.get(name)
        lxd_project.description = description
        lxd_project.save()

        _logger.info("Project '{}' updated".format(name))
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


@task
def delete(c, name):
    """Delete a Project.

    Delete an empty project.

    Arguments:
        name {str} -- Name of the project to delete.
    """

    message = "⚠ This operation can't be undone!\n"
    message += "Do you want delete the project '{}' ? (y, yes):".format(name)
    yes = input(message)

    if yes.lower() not in ['y', 'yes']:
        _logger.error("Abort")
        return

    client = lxdLib.get_pylxd_client(c)
    try:
        lxd_project = client.projects.get(name)
        lxd_project.delete()

        _logger.info("Project '{}' deleted".format(name))
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


@task
def use_project(c, project):
    """Save default project for the current user.

    Arguments:
        project {str} -- set project to use for next commands.
    """
    client = lxdLib.get_pylxd_client(c)
    projectLib.check_project(client, project)
    projectLib.set_user_default_project(c, project)


projectCollection.add_task(init_default)
projectCollection.add_task(list)
projectCollection.add_task(create)
projectCollection.add_task(update)
projectCollection.add_task(delete)
projectCollection.add_task(use_project, 'use')
