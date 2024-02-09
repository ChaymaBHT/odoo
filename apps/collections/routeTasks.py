# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from apps.lib import containerLib, lxdLib, projectLib, routeLib, utils
from invoke import Collection, task

routeCollection = Collection('route')


@task
def list(c):
    """List all runbot route.

    List all Traefik configuration.
    """
    client = lxdLib.get_pylxd_client(c, "default")
    proxy = client.instances.get(c.proxy_server_name)
    containerLib.execute(c, proxy, [
        'ls',
        '-l',
        '/etc/traefik/conf.d',
    ])


@task
def set(c, name, project='', slug=""):
    """Set new runbot route.

    The slug is the prefix of the url.

    By exemple for eezee-it.test.eezee-box.com, with the slug "test"
    the url is:  test.eezee-it.test.eezee-box.com

    Arguments:
        name {str} -- Runbot Name

    Keyword Arguments:
        project {str} -- The project Name (default: {''})
        slug {str} -- The url prefix (default: {""})
    """
    project = projectLib.get_project(c, project)
    name = utils.get_slug(name)
    container = containerLib.get_container_name(name, project)

    if not slug:
        slug = name

    routeLib.set_route(c, project, container, slug)


@task
def show(c, name, project=''):
    """Show route configuration.

    Diplay the Traefik configuration.

    Arguments:
        name {str} -- Runbot Name

    Keyword Arguments:
        project {str} -- The Project Name (default: {''})
    """
    project = projectLib.get_project(c, project)
    container_name = containerLib.get_container_name(name, project)

    client = lxdLib.get_pylxd_client(c, "default")
    proxy = client.instances.get(c.proxy_server_name)
    containerLib.execute(c, proxy, [
        'cat',
        '/etc/traefik/conf.d/{}_odoo.toml'.format(container_name),
    ])


@task
def delete(c, name, project=''):
    """Delete the runbot route.

    Delete the route (url) of a runbot.

    Arguments:
        name {name} -- Runbot name

    Keyword Arguments:
        project {str} -- The project name (default: {''})
    """
    project = projectLib.get_project(c, project)
    name = utils.get_slug(name)
    container = containerLib.get_container_name(name, project)

    routeLib.delete_route(c, container)


routeCollection.add_task(list)
routeCollection.add_task(set)
routeCollection.add_task(show)
routeCollection.add_task(delete)
