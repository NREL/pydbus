"""
Command line interface
"""

import logging

import click
import time

from ._version import __version__
from .agents.dbus import DBusAgent
from .log import setup_logger

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__, '--version')
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    """command line interface"""
    if debug:
        setup_logger()

@cli.command()
@click.option('--name', prompt='name:', help='Name of the DBus Agent')
def run(name):
    """run DBus agent"""
    logger.debug("Running a DBus Agent with name {name}".format(name=name))
    agent = DBusAgent(name=name)

    while True:

        logger.debug("Requesting component information %s", agent._request_component_information())
        logger.debug("Sleeping for 1 second")
        time.sleep(1)



if __name__ == "__main__":

    cli(True)
