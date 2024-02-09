# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import sys

_logger = logging.getLogger('tasks')


def check_environment(environment):
    """Check if environment is correct.

    Arguments:
        environment {str} -- Environment to check.
    """
    if not environment:
        return

    available_envs = ['demo', 'dev', 'staging', 'production']
    if environment not in available_envs:
        _logger.error('Environment "{}" not valide! (used on of: {})'.format(
            environment, ", ".join(available_envs)))
        sys.exit(1)


def get_default_environment(c, project):
    """Get the default environment.

    If project config has the key "default_environment", return
    this environment.

    If not project in config or not key "default_environment" on project
    config, return the "default_env" config value.

    Arguments:
        c {[type]} -- [description]
        project {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    project_env = False
    if project and project in c.projects:
        project_env = c.projects[project].get('default_environment', False)

    if project not in c.projects:
        _logger.warning("Project not found on configuration file.")

    return project_env or c.default_env


def get_env_from_profiles(profiles):
    """If a profile is a environment, return the profile name.

    Environment is defined with an LXD Profile.

    Arguments:
        profiles {list} -- list of profile to check.

    Returns:
        [str] -- environment
    """
    available_envs = ['demo', 'dev', 'staging', 'production']

    for profile in profiles:
        if profile in available_envs:
            return profile
