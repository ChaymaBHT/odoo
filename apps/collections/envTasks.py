# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from invoke import Collection, task
from tabulate import tabulate

_logger = logging.getLogger('tasks')

envCollection = Collection('env')


@task
def list(c):
    """List Odoo environments (dev, staging, production, demo).

    Environments are compatibled with Odoo.sh:

    * dev: for development instances (developper branchs)
    * staging: for staging instances (Test/Staging branchs)
    * production: for production instances (Production branchs)

    Extra environment for Eezee-It:

    * demo: for instances dedicated for a demo or a poc
    """
    envs = []
    for profile in c.profiles:
        if not profile['is_env']:
            continue

        envs.append([
            profile['name'],
            profile['description'],
        ])

    print(tabulate(envs, headers=[
        "Name",
        "Description",
    ], tablefmt="orgtbl"))


envCollection.add_task(list)
