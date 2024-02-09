# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from io import StringIO

_log = logging.getLogger('tasks')


def _run_command(c, command, pty=False, **args):
    full_command = " ".join(command)

    if isinstance(command, str):
        command = [command]

    if c.debug:
        _log.debug(full_command)

    default_args = {
        'pty': pty
    }

    command_args = {**default_args, **args}

    c.run(full_command, **command_args)


def _get_command_result(c, command, **args):
    result = StringIO()
    error_stream = StringIO()

    if isinstance(command, str):
        command = [command]

    full_command = " ".join(command)
    if c.debug:
        _log.debug(full_command)

    args['out_stream'] = result

    c.run(full_command, **args)

    value = result.getvalue().strip()

    if c.debug:
        _log.debug('=> Result: {}'.format(value))

    return value
