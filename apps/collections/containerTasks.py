# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import sys
import time

import humanize
from apps.invoke import _run_command
from apps.lib import (appLib, containerLib, envLib, lxdLib, profileLib,
                      projectLib, routeLib, utils)
from dateutil.parser import isoparse
from invoke import task
from pylxd.exceptions import NotFound
from tabulate import tabulate

_logger = logging.getLogger('tasks')


try:
    from pylxd.exceptions import LXDAPIException
except (ImportError, IOError) as err:
    _logger.debug(err)


@task
def list(c, project='', verbose=False):
    """List all runbots instances for a project.

    Keyword Arguments:
        project {str} -- The project to list instances (default: {''})
    """
    project = projectLib.get_project(c, project)
    project_config = projectLib.get_project_config(c, project)
    project_url = project_config.get('url', '')
    client = lxdLib.get_pylxd_client(c, project)
    instances = []
    instances_lxd = client.instances.all()

    for instance in instances_lxd:
        env = envLib.get_env_from_profiles(instance.profiles)

        status = instance.status
        if verbose:
            status += ' ({})'.format(instance.status_code)

        instance_name = instance.name.replace(
            "?project={}".format(project), '').replace('{}-'.format(project), '', 1)
        instance_data = [
            instance_name,
            instance.description,
            status,
            'https://{}.{}'.format(instance_name, project_url),
            env,
            humanize.naturalsize(instance.state().memory['usage']),
            isoparse(instance.created_at).strftime('%d %b %Y %H:%M:%S')
        ]

        if verbose:
            instance_data.append(", ".join(instance.profiles))

        instances.append(instance_data)

    headers = [
        "Name",
        "Description",
        "Status",
        "Url",
        "Environment",
        "Memory",
        "Created at",
    ]

    if verbose:
        headers.append("LXD Profiles")
    print(tabulate(instances, headers=headers, tablefmt="orgtbl"))


@task
def execute(c, name, command, project=''):
    """Execute a bash command.

    Execute a shell command as Odoo user.

    Arguments:
        name {str} -- Runbot Name
        command {str} -- Command to execute

    Keyword Arguments:
        project {str} -- The project Name (default: {''})
    """
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(name, project)

    try:
        instance = client.instances.get(container_name)
        print(str(containerLib.execute(c, instance, command.split(' '),
                                       user='odoo')))

    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


# @task
# def set_env(c, name, key, value, project=''):
#     project = projectLib.get_project(c, project)
#     client = lxdLib.get_pylxd_client(c, project)
#     container_name = containerLib.get_container_name(name, project)
#     instance = client.instances.get(container_name)
#     containerLib._set_envs(instance, {
#         key: value
#     })


@task
def shell(c, name, project='', user='odoo'):
    """Access to the instance.

    Only work on a locate LXD server.

    Arguments:
        name {str} -- The name of the instance to access

    Keyword Arguments:
        project {str} -- The project instance (default: {''})
    """
    if c.remote:
        # Check ws4py.client or Tornado
        # project = projectLib.get_project(c, project)
        # client = lxdLib.get_pylxd_client(c, project)
        # container_name = containerLib.get_container_name(name, project)
        # instance = containerLib.get_instance(client, container_name)
        # res = instance.raw_interactive_execute(['/bin/bash'])
        # lxc_url = c.remote_endpoint.replace('https://', 'wss://')
        # print(lxc_url + res['ws'])
        _logger.error("Only available for a local access.")
        sys.exit(1)

    project = projectLib.get_project(c, project)
    container_name = containerLib.get_container_name(name, project)

    if user == 'root':
        _run_command(c, [
            'lxc shell',
            container_name,
            "--project {}".format(project),
        ], pty=True)

        return

    _run_command(c, [
        'lxc exec',
        container_name,
        "--project {}".format(project),
        "-- sudo -H -i -u {} bash".format(user),
    ], pty=True)


@task
def create(c, name, version='', image='', project='', slug='', root=False,
           env='', app='', with_post_command=True):
    """Create a new Runbot (with route).

    Create a new Runbot by an Odoo version or an Lxd image.

    The slug corresponding to the url prefix for the runbot url.

    The app, can be pass or the project app is used or the default app.

    Arguments:
        name {str} -- New runbot name

    Keyword Arguments:
        version {str} -- Odoo version (13.0, 14.0, 15.0, ...) (default: {''})
        image {str} -- Lxd image (cannot be used with version) (default: {''})
        project {str} -- The project Name (default: {''})
        slug {str} -- Url prefix for the runbot (default: {''})
        root {bool} -- Not Fully implemented (no slug) (default: {False})
        env {str} -- Environment to use (dev, staging, production, demo)
           (default: {''})
        app {str} -- Define the app to use to install (default: {''})
    """
    project = projectLib.get_project(c, project)
    url = utils.get_url(c, name, slug, project, root)
    name = utils.get_slug(name)
    container_name = containerLib.get_container_name(name, project)
    app = appLib.get_app(c, app, project)

    if not env:
        env = envLib.get_default_environment(c, project)
    envLib.check_environment(env)

    if not slug:
        slug = name

    if image and version:
        _logger.error("You can specify an image and a version!")
        sys.exit(1)

    if not image and not version:
        _logger.error("You should specify an image or a version!")
        sys.exit(1)

    if version:
        image = appLib.get_app_image_alias(c, app, version)

    image_lxd = _get_lxd_image(c, image, project)

    profiles = profileLib.get_profiles(c, project, env, app)

    linux_environments = {
        'ODOO_STAGE': env,
        'ODOO_SLUG': slug,
    }

    if version:
        linux_environments['ODOO_VERSION'] = version

    _logger.info("Creating {}, the operation can take a long time.".format(
        name))
    instance = containerLib.create_container(
        c, container_name, image, project, profiles, linux_environments)

    _logger.info("Adding route.")
    routeLib.set_route(c, project, container_name, slug=slug)

    if with_post_command:
        project_config = projectLib.get_project_config(c, project)
        _logger.info("Waiting for the availability of the new runbot..")
        time.sleep(10)
        containerLib._execute_post_commands(c, instance, app, dict(
            project=project,
            project_upper=project.upper(),
            slug=slug,
            name=name,
            version=version,
            env=env,
            project_url=project_config.get('url', ''),
            container_url="{}.{}".format(slug, project_config.get('url', '')),
        ))

    if not env:
        env = envLib.get_env_from_profiles(profiles)

    instance_data = [
        ["Name", name],
        ["Url", url],
        ["Container Name", container_name],
        ["Image used", image_lxd.aliases[0]['name']],
        ["Environment", env],
        ["LXD Profiles", ", ".join(profiles)],
    ]

    if project:
        instance_data.append(["LXD project", project])

    if version:
        instance_data.append(["Odoo version", version])

    print(tabulate(instance_data, tablefmt="orgtbl"))


@task
def execute_post_command(c, name, version, project='', app='', env=''):
    message = "⚠ This operation can be reset some configuration!\n"
    message += "Do you want execute the post common on the runbot '{}' for the project '{}' ? (y, yes):".format(
        name, project)
    yes = input(message)

    if yes.lower() not in ['y', 'yes']:
        _logger.error("Abort")
        return

    project_config = projectLib.get_project_config(c, project)
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(name, project)
    instance = containerLib.get_instance(client, container_name)
    app = appLib.get_app(c, app, project)
    name = utils.get_slug(name)

    containerLib._execute_post_commands(c, instance, app, dict(
        project=project,
        project_upper=project.upper(),
        slug=name,
        name=name,
        version=version,
        env=env,
        project_url=project_config.get('url', ''),
        container_url="{}.{}".format(name, project_config.get('url', '')),
    ))


@task
def copy(c, name, target_name, project='', slug='', env=""):
    """Copy a runbot.

    Copy a runbot, with btrfs, not all adata is copied but only index.
    A new route is created fot the new runbot.

    Decorators:
        task

    Arguments:
        name {str} -- Runbot to copy
        target_name {str} -- Target Runbot

    Keyword Arguments:
        project {str} -- [The project of the Runbot] (default: {''})
        slug {str} -- [Alternative url prefix] (default: {the runbot name})
        env {str} -- [Runbot environment] (default: {False})
    """
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(name, project)
    target_container_name = containerLib.get_container_name(
        target_name, project)

    slug = slug and utils.get_slug(slug) or utils.get_slug(target_name)

    if not env:
        env = envLib.get_default_environment(c, project)

    envLib.check_environment(env)

    if not client.instances.exists(container_name):
        _logger.error("Runbot {} doesn't exists!".format(container_name))
        sys.exit(1)

    if client.instances.exists(target_container_name):
        _logger.error("Runbot {} already exists!".format(target_name))
        sys.exit(1)

    profiles = profileLib.get_profiles(c, project, env, 'odoo')
    config = {
        'name': target_container_name,
        'source': {
            'type': 'copy',
            'source': container_name
        },
        'profiles': profiles
    }
    _logger.info("Creating the new instance..")
    instance = client.instances.create(config, wait=True)

    _logger.info("Starting the new instance..")
    instance.start()

    _logger.info("Creating the route..")
    routeLib.set_route(c, project, target_container_name, slug=slug)

    url = utils.get_url(c, target_container_name, slug, project, False)
    instance_data = [
        ["Name", name],
        ["Url", url],
    ]
    print(tabulate(instance_data, tablefmt="orgtbl"))
    return instance


@task
def deploy(c, name, branch, source_name='', project='', slug='',
           update_all=False, env=''):
    """Deploy a new code to a runbot.

    If the container doesn't exist and source name is set,
    a new runbot is created based on the source_name.

    By default the update is made on auto addons detections, bases on
    git diff and addons versions.

    Arguments:
        name {str} -- The runbot to deploy
        branch {str} -- [The branche to deploy]

    Keyword Arguments:
        source_name {str} -- [Source container to copy] (default: {''})
        project {str} -- [The runbot project] (default: {''})
        slug {str} -- [Url prefix to use] (default: {The name})
        update_all {bool} -- [Update all module?] (default: {False})
        env {str} -- [Runbot environment] (default: {False})
    """

    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(
        name, project)
    slug = slug and utils.get_slug(slug) or utils.get_slug(name)

    _logger.info("Deploying branch '{}' on project {}".format(branch, project))

    if not client.instances.exists(container_name):
        _logger.info("Runbot '{}' doesn't exists, creating it from {} using env {}".format(
            name, source_name, env))
        instance = copy(c, source_name, name, env=env, slug=slug, project=project)
    else:
        _logger.info("Using Runbot '{}'".format(name))
        instance = containerLib.get_instance(client, container_name)

    command = [
        'odoo',
        'upgrade',
        '--force',
        '--branch',
        branch
    ]

    if not update_all:
        command.append('--auto')

    print(str(containerLib.execute(c, instance, command, user='odoo')))


@task
def set_env(c, name, env, project=''):
    """Update instance environment (dev, staging, production, demo).

    Update the environment of Runbot.

    Arguments:
        name {str} -- runbot name
        env {str} -- environment name

    Keyword Arguments:
        project {str} -- The runbot project (default: {''})
    """
    envLib.check_environment(env)
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)

    container_name = containerLib.get_container_name(name, project)
    instance = containerLib.get_instance(client, container_name)
    # Todo don't harcode 'odoo'
    profiles = profileLib.get_profiles(c, project, env, 'odoo')
    instance.profiles = profiles
    instance.save()


@task
def delete(c, name, project='', force=False):
    """Delete a runbot.

    Delete a runbot for a specific project or for the
    the default project.

    Arguments:
        name {str} -- The runbot to delete

    Keyword Arguments:
        project {str} -- The name of the runbot project (default: {''})
        force {bool} -- Don't confirm to delete (default: {False})
    """
    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)
    container_name = containerLib.get_container_name(name, project)

    if not force:
        message = "⚠ This operation can't be undone!\n"
        message += "Do you want delete the runbot '{}' on the project '{}' ? (y, yes):".format(
            name, project)
        yes = input(message)

        if yes.lower() not in ['y', 'yes']:
            _logger.error("Abort")
            return

    try:
        instance = client.instances.get(container_name)

        if instance.status_code == 103 or instance.status_code == 110:
            _logger.info("Stopping {}".format(name))
            instance.stop()
            time.sleep(3)

        instance.delete(wait=True)
        routeLib.delete_route(c, container_name)
        _logger.info("Runbot {} deleted".format(name))

    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


def _get_lxd_image(c, image_name, project):
    client = lxdLib.get_pylxd_client(c, project)
    try:
        return client.images.get_by_alias(image_name)
    except NotFound:
        _logger.error("Image '{}' not found !".format(image_name))
        sys.exit(1)
