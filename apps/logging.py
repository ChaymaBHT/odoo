# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

import colorama

colorama.init()
LOG_COLORS = {
    logging.ERROR: colorama.Fore.RED,
    logging.WARNING: colorama.Fore.YELLOW,
    logging.INFO: colorama.Fore.GREEN,
    logging.DEBUG: colorama.Fore.MAGENTA,
}


class ColorFormatter(logging.Formatter):

    def __init__(self, format="%(message)s"):
        """Create a new formatter that adds colors"""
        super(ColorFormatter, self).__init__(format)

    def format(self, record, *args, **kwargs):
        if record.levelno in LOG_COLORS:
            record.msg = LOG_COLORS[record.levelno] \
                + record.msg + colorama.Style.RESET_ALL
        return super(ColorFormatter, self).format(record, *args, **kwargs)
