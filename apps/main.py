# Copyright 2022      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import os

from apps.__about__ import __version__
from apps.collections import containerMgrTasks, containerTasks
from apps.collections.apiTasks import apiCollection
# from apps.collections.envTasks import envCollection
from apps.collections.envTasks import list as env_list
from apps.collections.imageTasks import apps, imageCollection
from apps.collections.profileTasks import profileCollection
from apps.collections.projectTasks import list as project_list
from apps.collections.projectTasks import projectCollection, use_project
from apps.collections.routeTasks import routeCollection, set
from apps.collections.storageTasks import storageCollection
from apps.logging import ColorFormatter
from invoke import Collection, Program
from invoke.config import Config, merge_dicts

_log = logging.getLogger('tasks')
_output = logging.StreamHandler()
_output.setFormatter(ColorFormatter())
_log.addHandler(_output)
_log.setLevel(logging.DEBUG)


class InvokeConfig(Config):
    prefix = 'runbot'
    file_prefix = 'runbot'

    def __init__(self):

        super(InvokeConfig, self).__init__()
        self.set_project_location(os.getcwd())
        self.load_project()

    @staticmethod
    def global_defaults():
        their_defaults = Config.global_defaults()
        my_defaults = {
            'debug': False,
            'proxy_server_name': 'proxy',
            'remote': False,
            'remote_endpoint': '',
            'projects': {
                'runbot': {
                    'url': '',
                    'description': "Default project to store runbot instances",
                    'disabled': False,
                },
                'demo': {
                    'url': '',
                    'default_environment': 'demo',
                    'description': "Project to store demo instances",
                    'disabled': False,
                }
            },
            'default_env': 'dev',
            'default_app': 'odoo',
            'local_keys_folder': '~/.ssh',
            'local_key_prefix': 'runbot_lxd',
            'default_project': 'runbot',
            'applications': {
                'odoo': {
                    'versions': {
                        '12.0': {
                            'image_alias': 'debian-10-odoo-12-0',
                            'description': 'Eezee-It: Debian 10 - Odoo 12.0',
                        },
                        '13.0': {
                            'image_alias': 'debian-10-odoo-13-0',
                            'description': 'Eezee-It: Debian 10 - Odoo 13.0',
                        },
                        '14.0': {
                            'image_alias': 'debian-10-odoo-14-0',
                            'description': 'Eezee-It: Debian 10 - Odoo 14.0',
                        },
                        '15.0': {
                            'image_alias': 'debian-10-odoo-15-0',
                            'description': 'Eezee-It: Debian 10 - Odoo 15.0',
                        }
                    },
                    'required_profiles': [
                        'default',  # for disk storage
                        'odoo',
                    ],
                    'post_create_commands': [
                        {
                            'type': 'shell',
                            'commands': [
                                {
                                    'title': 'Update Odoo community',
                                    'command': 'git -C odoo/community pull',
                                }, {
                                    'title': 'Update Odoo enterprise',
                                    'command': 'git -C odoo/enterprise pull',
                                }, {
                                    'title': 'Update eezee-box',
                                    'command': 'git -C eezee-box/ pull',
                                    'environments': {
                                        'GIT_SSH_COMMAND': "ssh -i ~/.ssh/id_enterprise -o IdentitiesOnly=yes"
                                    }
                                }, {
                                    'title': 'Create addons directory',
                                    'command': 'mkdir -p addons-${project_upper}',
                                }, {
                                    'title': 'Create odoomgr config file',
                                    # Normally Odoo stage should not be passed there
                                    'command': 'odoo scaffold --project-name ${project} --project-directory addons-${project_upper} --version ${version}',
                                    'environments': {
                                        'ODOO_STAGE': '${env}'
                                    }
                                }, {
                                    'title': 'Init new database',
                                    'command': 'odoo init --force',
                                }, {
                                    'title': 'Install Eezee-box addons',
                                    'command': 'odoo install -a eezee_about,eezee_auth_sso,eezee_maintenance_cost --no-http',
                                }, {
                                    'title': 'Change admin and master password',
                                    'command': 'odoo protect --force'
                                }

                            ]
                        }
                    ],
                    'user': {
                        'name': 'odoo',
                        'uid': 4001,
                        'home': '/opt/local/odoo',
                    }
                }
            },
            'profiles': [{
                'name': 'demo',
                'is_env': True,
                'description': 'Demo instances',
                'cpu_limit': '2',
                'memory_limit': '4GB',
                'environment': {
                    'ODOO_STAGE': 'demo'
                },
            }, {
                'name': 'odoo',
                'is_env': False,
                'description': 'Odoo instances',
                'cpu_limit': '2',
                'memory_limit': '4GB',
            }, {
                'name': 'dev',
                'is_env': True,
                'description': 'Development instances',
                'cpu_limit': '2',
                'memory_limit': '4GB',
            }, {
                'name': 'staging',
                'is_env': True,
                'description': 'Staging instances',
                'cpu_limit': '2',
                'memory_limit': '4GB',
            }, {
                'name': 'production',
                'is_env': True,
                'description': 'Production instances',
                'cpu_limit': False,
                'memory_limit': False,
            }],
        }

        return merge_dicts(their_defaults, my_defaults)


ns = Collection.from_module(containerTasks)
ns.add_task(project_list, 'projects')
ns.add_task(env_list, 'envs')
ns.add_task(apps)
ns.add_task(use_project, 'use')
ns.add_task(set, 'set-route')
# ns.add_collection(envCollection)

ns_manager = Collection.from_module(containerMgrTasks)
ns_manager.add_collection(apiCollection)
ns_manager.add_collection(imageCollection)
ns_manager.add_collection(profileCollection)
ns_manager.add_collection(storageCollection)
ns_manager.add_collection(projectCollection)
ns_manager.add_collection(routeCollection)

program = Program(config_class=InvokeConfig, namespace=ns, version=__version__)
program_manager = Program(config_class=InvokeConfig, namespace=ns_manager,
                          version=__version__)
