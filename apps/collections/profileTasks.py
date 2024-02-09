# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging
import sys

from apps.lib import lxdLib, utils
from invoke import Collection, task
from tabulate import tabulate

_logger = logging.getLogger('tasks')


try:
    from pylxd.exceptions import LXDAPIException
except (ImportError, IOError) as err:
    _logger.debug(err)

profileCollection = Collection('profile')


@task
def list(c):
    """List LXD Profile.

    LXD Profile allow to manage by exemple limit
    on a container like memory and CPU limit.

    If many profiles are on a container, the limit
    is set for the first profile found (if limit defined
    on it)

    Each env have a profile with the same name.
    """
    client = lxdLib.get_pylxd_client(c)
    profiles = []
    profiles_lxd = client.profiles.all()

    for profile in profiles_lxd:
        profiles.append(_get_data_profile_to_show(profile))

    _show_profile(profiles)


@task
def create(c, name, description='', cpu_limit='', memory_limit=''):
    """Create a new profile.

    * For CPU indicate the number of CPU (1, 2, 3)
    * For memory indicate the amount and the unit of mesure
      exe: 3GB

    Arguments:
        name {str} -- Profile name

    Keyword Arguments:
        description {str} -- Description of the profile (default: {''})
        cpu_limit {str} -- Limit CPU for container attached on this profile
        (default: {''})
        memory_limit {str} -- Limit memory for container attached on this
        profile (default: {''})
    """
    profile = _create(c, name, description, cpu_limit, memory_limit)
    _show_profile([_get_data_profile_to_show(profile)])


@task
def delete(c, name):
    """Delete a profile.

    Arguments:
        name {[str]} -- Name of the profile to delete
    """
    client = lxdLib.get_pylxd_client(c)
    name = utils.get_slug(name)

    message = "⚠ This operation can't be undone!\n"
    message += "Do you want delete the profile '{}' ? (y, yes):".format(name)
    yes = input(message)

    if yes.lower() not in ['y', 'yes']:
        _logger.error("Abort")
        return

    try:
        profile = client.profiles.get(name)
        profile.delete()

        _logger.info("Profile '{}' deleted.".format(name))
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


@task
def update(c, name, new_name='', description='', cpu_limit='',
           memory_limit=''):
    """Update a profile (name, description and limits).

    * For CPU indicate the number of CPU (1, 2, 3)
    * For memory indicate the amount and the unit of mesure
      exe: 3GB

    Arguments:
        name {str} -- name of the profile to update

    Keyword Arguments:
        new_name {str} -- New name for the profile (default: {''})
        description {str} -- New description for the profile (default: {''})
        cpu_limit {str} -- Limit CPU for container attached on this profile
        (default: {''})
        memory_limit {str} -- Limit memory for container attached on this
        profile (default: {''})
    """
    client = lxdLib.get_pylxd_client(c)
    name = utils.get_slug(name)

    try:
        profile = client.profiles.get(name)

        if new_name:
            profile.rename(new_name)

        config = {}

        if cpu_limit:
            config['limits.cpu'] = cpu_limit

        if memory_limit:
            config['limits.memory'] = memory_limit

        if config:
            profile.config.update(config)

        if description:
            profile.description = description

        if config or description:
            profile.save()

        _logger.info("Profile '{}' updated.".format(name))
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


@task
def init_default(c):
    """Init default profiles.

    This subcommand create profiles defined on the configuration file.
    For exemples see on the main.py file.
    """
    client = lxdLib.get_pylxd_client(c)

    for profile in c.profiles:
        try:
            name = utils.get_slug(profile["name"])
            profile = client.profiles.get(name)
            profile
        except LXDAPIException:
            _create(c, profile["name"], profile["description"],
                    profile["cpu_limit"], profile["memory_limit"])

    list(c)


def _create(c, name, description='', cpu_limit='', memory_limit=''):
    client = lxdLib.get_pylxd_client(c)

    config = {}

    if cpu_limit:
        config['limits.cpu'] = cpu_limit

    if memory_limit:
        config['limits.memory'] = memory_limit

    try:
        profile = client.profiles.create(
            name=utils.get_slug(name),
            config=config,
        )

        if description:
            profile.description = description
            profile.save()

        return profile
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


def _get_data_profile_to_show(profile):
    return [
        profile.name,
        profile.description,
        'limits.cpu' in profile.config and profile.config['limits.cpu']
        or 'No limit',
        'limits.memory' in profile.config and profile.config['limits.memory']
        or 'No limit',
    ]


def _show_profile(profiles):
    print(tabulate(profiles, headers=[
        "Name",
        "Description",
        "CPU Limit",
        "Memory Max",
    ], tablefmt="orgtbl"))


profileCollection.add_task(list)
profileCollection.add_task(init_default)
profileCollection.add_task(create)
profileCollection.add_task(delete)
profileCollection.add_task(update)
