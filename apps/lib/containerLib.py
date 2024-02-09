# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import sys
from string import Template

from apps.lib import appLib, lxdLib, projectLib, utils

_logger = logging.getLogger('tasks')

try:
    from pylxd.exceptions import LXDAPIException
except (ImportError, IOError) as err:
    _logger.debug(err)


def get_instance(client, container_name):
    try:
        return client.instances.get(container_name)
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


def get_container_name(name, project=''):
    """get the container name of a runbot.

    If the project is 'default', keep the runbot name.
    if the project is not 'default' concatenate the
    project with the runbot name like %project%-%name%.

    Project is prefixed because lxd use the container name
    on the internal dns, by exemple %name%.lxd, because each
    project share the internal dns, two containes can't have the
    same nale.

    Arguments:
        name {str} -- container name

    Keyword Arguments:
        project {str} -- The project name (default: {''})

    Returns:
        str -- The containe name of the runbot.
    """
    if project and project != 'default':
        name = '{}-{}'.format(project, name)

    # Lxd doesn't allow a name starting with a digit.
    if name[0].isdigit():
        name = 'o' + name

    return utils.get_slug(name)


def create_container(c, name, image_alias, project, profiles,
                     environments={}):
    """Create a new container.

    Todo: add the documentation.

    Arguments:
        name {str} -- Runbot name
        image_alias {str} -- LXD image alias
        project {str} -- Project name
        profiles {list} -- list of profile to add on the new container.

    Keyword Arguments:
        environments {dict} -- Linux environments to add on the container
           (default: {{}})
    """

    project = projectLib.get_project(c, project)
    client = lxdLib.get_pylxd_client(c, project)

    config = {
        'name': name,
        'source': {
            'type': 'image',
            'alias': image_alias
        },
        'profiles': profiles
    }

    try:
        instance = client.instances.create(config, wait=True)
        _logger.info("Starting the new instance")
        instance.start(wait=True)

        # if environments:
        # _logger.info("Updating env variable.")
        # _set_envs(instance, environments)
        return instance
    except LXDAPIException as e:
        _logger.error(str(e))
        sys.exit(1)


def _execute_post_commands(c, instance, app, data, key='post_create_commands'):
    """Execute post command on a instance.

    Use the python standard Template Class

    On the template string, the formt is:
        * ${who} likes ${what} => where who and what is a data key

    Arguments:
        instance {Client} -- LXD Instance
        app {str} -- app installed
        data {dict} -- a list key => value to pass to the command

    Keyword Arguments:
        key {str} -- The post command config name
            (default: {'post_create_commands'})
    """
    app_config = appLib.get_application_config(c, app)
    user = app_config.get('user', {}).get('name')
    user = user or 'odoo'
    post_commands = app_config.get(key)
    if not post_commands:
        return

    for post_command in post_commands:
        type = post_command['type']
        if type == 'shell':
            for subcommand in post_command['commands']:
                title = Template(subcommand['title'])
                command = Template(subcommand['command'])
                environments = subcommand.get('environments', {})

                try:
                    title = title.substitute(data)
                    _logger.info(title)
                    command = command.substitute(data)

                    for environment in environments:
                        env_t = Template(environments[environment])
                        environments[environment] = env_t.substitute(data)

                    execute(c, instance, command.split(" "), user=user,
                            environments=environments)
                except ValueError as e:
                    _logger.error(str(e))
                    sys.exit(1)


def execute(c, instance, command, environments={}, user='root'):
    """Execute a shell command on a instance.

    Command should be a list, by exemple:
       * ['ls', '-l']
       *

    Each space should be on a new item of the list.

    Arguments:
        instance {str} -- The Lxd Container instance
        command {list} -- Command as list

    Keyword Arguments:
        user {str} -- User to execute the command (default: {odoo})
    """

    uid = None
    cwd = None
    if user == 'odoo':
        uid = 4001
        cwd = '/opt/local/odoo'

    if c.debug:
        _logger.debug("Running the commande => {}".format(" ".join(command)))
        if environments:
            _logger.debug("With environment variables => {}".format(
                environments))

    exit_code, stdout, stderr = instance.execute(
        command, stdout_handler=sys.stdout.write,
        stderr_handler=sys.stderr.write, user=uid, cwd=cwd, environment=environments)
    if exit_code or stderr:
        _logger.error("{} - {}".format(exit_code, stderr))
        sys.exit(exit_code)

    return stdout


def _set_envs(instance, environments):
    """Set Linux environment on the container.

    Environment is set on the file /etc/profile.d/odoo.sh

    Arguments:
        instance {Client} -- Lxd container instance
        environments {dict} -- Dict of key => value to add.
    """
    profile_file = '/etc/profile.d/odoo.sh'
    command = [
        "/usr/bin/echo",
        "-n",
        ">",
        profile_file
    ]
    print(str(" ".join(command)))

    exit_code, stdout, stderr = instance.execute(command)
    if stderr:
        _logger.error(stderr)

    for env in environments:

        command = [
            'sed',
            '-i',
            '/^{}/d'.format(env),
            '/etc/profile.d/odoo.sh'
        ]
        print(str(" ".join(command)))
        exit_code, stdout, stderr = instance.execute(command)
        if stderr:
            _logger.error(stderr)
        command = [
            '/usr/bin/echo',
            "'export",
            '{}="{}"\''.format(env, environments[env].replace(
                '"', '').replace("'", '')),
            '>',
            "/etc/profile.d/odoo.sh"
        ]
        print(str(" ".join(command)))
        exit_code, stdout, stderr = instance.execute(command)
        if stderr:
            _logger.error(stderr)
