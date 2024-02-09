# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import sys

from apps.lib import projectLib

_logger = logging.getLogger('tasks')


def get_app(c, app, project=''):
    """Get the app name.

    If app defined, return the app.
    if not defined app is search on project and
    on configuration.

    Arguments:
        app {str} -- App to get (can be empty)

    Keyword Arguments:
        project {str} -- Project Name of the runbot (default: {''})

    Returns:
        [str] -- The real name of the app
    """
    # If app defined return the app
    if app:
        return check_app(c, app)

    # if app not defined check on project
    config = projectLib.get_project_config(c, project)
    default_app_project = config.get('default_app', False)
    if project and default_app_project:
        return check_app(c, default_app_project)

    # if no app defined or not app in project, return default app
    return check_app(c, c.default_app)


def check_app(c, app):
    """Check if the app is referenced on the configuration file.

    Arguments:
        app {str} -- App name

    Returns:
        [str] -- The app name itself (for chaining)
    """
    if not c.applications.get(app, False):
        _logger.error("App '{}' is not available, see apps list.".format(app))
        sys.exit(1)

    return app


def get_application_config(c, app):
    """Return the application configuration."""
    check_app(c, app)
    return c.applications.get(app)


def get_app_image_alias(c, app, version):
    """Return the image alias corresponding to the app version."""
    app_config = get_application_config(c, app)
    version_data = app_config.get('versions', {}).get(version, False)

    if not version_data:
        _logger.error("Version '{}' not available for app the '{}'.".format(
            version, app))
        sys.exit(1)

    return version_data['image_alias']
