# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from apps.lib import containerLib, lxdLib, projectLib

_logger = logging.getLogger('tasks')


def set_route(c, project, container, slug=""):
    """Create a new route on the Proxy server.

    Route are define on the Proxy server (default project).
    The routing is made with Traefik.

    Arguments:
        project {str} -- The project
        container {str} -- instance name

    Keyword Arguments:
        slug {str} -- the url prefixe of the project (default: {""})
    """
    client = lxdLib.get_pylxd_client(c, "default")
    project_data = projectLib.get_project_config(c, project)

    if not slug:
        slug = container.replace("{}-".format(project), '')

    proxy = containerLib.get_instance(client, c.proxy_server_name)

    containerLib.execute(c, proxy, [
        'add-odoo-container.sh',
        '-c',
        container,
        '-h',
        project_data['url'],
        '-s',
        slug,
    ])


def delete_route(c, container):
    """Delete the container route."""
    client = lxdLib.get_pylxd_client(c, "default")
    proxy = client.instances.get(c.proxy_server_name)
    containerLib.execute(c, proxy, [
        'rm',
        '/etc/traefik/conf.d/{}_odoo.toml'.format(container)
    ])

    _logger.info("Route Deleted.")
