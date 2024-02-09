# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from apps.lib import lxdLib
from invoke import Collection, task
from tabulate import tabulate

_logger = logging.getLogger('tasks')

storageCollection = Collection('storage')


@task
def list(c):
    """List storage-pools.

    Storage pools can be local directory, or a partition
    with btrfs or ZFS file system.
    """
    client = lxdLib.get_pylxd_client(c)
    storage_pools = []
    storage_pools_lxd = client.storage_pools.all()

    for storage_pool in storage_pools_lxd:
        storage_pools.append([
            storage_pool.name,
            storage_pool.driver,
            'size' in storage_pool.config and storage_pool.config['size'] or '',
            'volatile.initial_source' in storage_pool.config and storage_pool.config[
                'volatile.initial_source'] or '',
            len(storage_pool.volumes.all())
        ])

    print(tabulate(storage_pools, headers=[
        "Name",
        "Driver",
        "Size",
        "Partion",
        "Used by",
    ], tablefmt="orgtbl"))


storageCollection.add_task(list)
