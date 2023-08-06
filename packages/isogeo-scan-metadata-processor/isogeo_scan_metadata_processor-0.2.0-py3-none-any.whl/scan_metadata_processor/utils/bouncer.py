# coding: utf-8
#! python3  # noqa: E265

"""
    Shortcuts to exit CLI properly and with pretty messages.

    Author: Isogeo
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# 3rd party
import click

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Functions #############
# ##################################


def exit_cli_error(message: str):
    """Terminates execution with error message.

    :param str message: message to log and display in terminal.
    """
    logger.error(message)
    click.secho(message=message, err=True, fg="red")
    click.Context.abort(message)


def exit_cli_normal(message: str):
    """Terminates execution with normal message (equivalent to INFO).

    :param str message: message to log and display in terminal.
    """
    logger.info(message)
    click.secho(message=message, err=False, fg="magenta")
    click.Context.abort(message)


def exit_cli_success(message: str):
    """Terminates execution with success message.

    :param str message: message to log and display in terminal.
    """
    logger.info(message)
    click.secho(message=message, err=False, fg="green")
    click.Context.abort(message)


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass
