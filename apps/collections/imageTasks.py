# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import sys

import humanize
from apps.lib import lxdLib
from dateutil.parser import isoparse
from invoke import Collection, task
from tabulate import tabulate

_logger = logging.getLogger('tasks')

try:
    from pylxd.exceptions import LXDAPIException
except (ImportError, IOError) as err:
    _logger.debug(err)

imageCollection = Collection('image')


@task
def list(c):
    """List LXD images.

    Images are used to create a new container.

    Keyword Arguments:
        project {str} -- [description] (default: {''})
    """
    client = lxdLib.get_pylxd_client(c)
    images = []
    images_lxd = client.images.all()

    for image in images_lxd:
        if not image.aliases:
            continue
        images.append([
            image.aliases[0]['name'],
            image.aliases[0]['description'],
            image.fingerprint,
            humanize.naturalsize(image.size),
            isoparse(image.uploaded_at).strftime('%d %b %Y %H:%M:%S'),
        ])

    print(tabulate(images, headers=[
        "Aliases",
        "Description",
        "Fingerprint",
        "Size",
        "Upload at",
    ], tablefmt="orgtbl"))


@task
def update(c, alias, description, new_alias=''):
    """Update image alias or image description.

    Arguments:
        alias {str} -- Alias of the image to update.
        description {str} -- New description.

    Keyword Arguments:
        new_alias {str} -- New Alias (default: {''})
    """
    client = lxdLib.get_pylxd_client(c)

    if not new_alias:
        new_alias = alias

    try:
        image = client.images.get_by_alias(alias)
        image.delete_alias(alias)
        image.save()
        image.add_alias(new_alias, description)
        _logger.info("Image '{}' updated.".format(alias))
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


@task
def apps(c, verbose=False):
    """List application with their version managed by the runbot.

    Each version of apps are stored on a lxd image.
    """
    client = lxdLib.get_pylxd_client(c)
    versions = []
    for application in c.applications:
        app_versions = c.applications[application]['versions']
        for version in app_versions:
            # Show only apps for image existing.
            try:
                client.images.get_by_alias(
                    app_versions[version]['image_alias'])
            except LXDAPIException:
                continue

            data = [
                application,
                version
            ]

            if verbose:
                data.append(app_versions[version]['image_alias'])
            versions.append(data)

    headers = [
        "Application",
        "Version",
    ]

    if verbose:
        headers.append("LXD image alias")
    print(tabulate(versions, headers=headers, tablefmt="orgtbl", disable_numparse=True))


imageCollection.add_task(list)
imageCollection.add_task(update)
