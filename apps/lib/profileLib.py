# Copyright 2022      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from apps.lib import appLib, envLib


def get_profiles(c, project, environment, app):
    """Return the profiles of a project.

    Each environment is defined with an LXD Profile.

    Return the environment or the default project environment.
    also return the required profiles define in the configuration
    file with the key "required_profiles" on apps

    Arguments:
        c {[type]} -- [description]
        project {[type]} -- [description]
        environment {[type]} -- [description]
    """
    environment = environment or envLib.get_default_environment(c, project)
    app_config = appLib.get_application_config(c, app)
    return [environment] + app_config.get('required_profiles', [])
