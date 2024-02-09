# Copyright 2022      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from apps.lib import projectLib
from slug import slug

_logger = logging.getLogger('tasks')


def get_slug(name):
    """Slug the name."""
    return slug(name.replace('.', '-'))


def get_url(c, name, slug, project, root):
    """Return a runbot url.

    If root:
       The url is composed of the url of the project

    if not root:
        The url is composed of the slug and the project url.

    if slug is empty, use the name.

    Arguments:
        name {str} -- Runbot name
        slug {str} -- url prefix
        project {str} -- The project
        root {bool} -- Check if the url is the root url.
    """
    project_data = projectLib.get_project_config(c, project)
    if root:
        return "https://{}".format(project_data['url'])

    url = get_slug(slug)
    if not url:
        url = get_slug(name)

    return "https://{}.{}".format(url, project_data['url'])
