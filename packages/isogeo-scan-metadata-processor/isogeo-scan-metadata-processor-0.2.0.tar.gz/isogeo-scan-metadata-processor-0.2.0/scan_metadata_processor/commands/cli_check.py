# coding: utf-8
#! python3  # noqa: E265


"""
    Sub-command in charge of checking settings and environment.

    Author: Isogeo
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from os import access, environ, getlogin, R_OK, W_OK
from pathlib import Path
from timeit import default_timer

# 3rd party library
import click
from isogeo_pysdk.checker import IsogeoChecker
from requests import Session

# submodules
from scan_metadata_processor.utils.proxies import proxy_settings
from scan_metadata_processor.utils.bouncer import exit_cli_error

# #############################################################################
# ########## Globals ###############
# ##################################

# chronometer
START_TIME = default_timer()

# logs
logger = logging.getLogger(__name__)

# default CLI context.
# See: https://click.palletsprojects.com/en/7.x/commands/#context-defaults
CONTEXT_SETTINGS = dict(obj={})

# #############################################################################
# ####### Command-line ############
# #################################
@click.command()
@click.pass_context
def check(cli_context: click.Context):
    """Perform checks about requirements: folders, network..."""
    logger.info("CHECK started after {:5.2f}s.".format(default_timer() - START_TIME))

    # extract values from CLI context
    logs_folder = cli_context.obj.get("FOLDER_LOGS")
    output_folder = cli_context.obj.get("FOLDER_OUTPUT")

    # -- CHECK FOLDERS PERMISSIONS -----------------------------------------------------
    if not access(logs_folder, W_OK):
        err_msg = "The LOGS folder is not writable by '{}': {}".format(
            getlogin(), logs_folder.resolve()
        )
        exit_cli_error(err_msg)

    if not access(output_folder, W_OK):
        err_msg = "The OUTPUT folder is not writable by '{}': {}".format(
            getlogin(), output_folder.resolve()
        )
        exit_cli_error(err_msg)

    input_folder = Path(environ.get("ISOGEO_MD_PROCESSOR_INPUT_FOLDER"))
    if not access(input_folder, R_OK):
        err_msg = "The INPUT folder is not readable by '{}': {}".format(
            getlogin(), input_folder.resolve()
        )
        exit_cli_error(err_msg)

    # -- DATABASE ----------------------------------------------------------------------
    if not Path(environ.get("ISOGEO_MD_PROCESSOR_DATABASE_FOLDER")).is_dir():
        logger.error(
            "Folder path for the database is not correct: {}".format(
                environ.get("ISOGEO_MD_PROCESSOR_DATABASE_FOLDER")
            )
        )
    database_folder = Path(environ.get("ISOGEO_MD_PROCESSOR_DATABASE_FOLDER"))

    try:
        database_folder.mkdir(parents=True, exist_ok=True)
        logger.info("Database folder: {}".format(database_folder))
    except PermissionError as e:
        msg_err = (
            "Impossible to create the output folder. Does the user '{}' ({}) have write permissions "
            "on the OUTPUT folder?. Original error: {}".format(
                environ.get("userdomain"), getlogin(), e
            )
        )
        exit_cli_error(msg_err)

    if not IsogeoChecker().check_is_uuid(environ.get("ISOGEO_GROUP_ID")):
        exit_cli_error("Isogeo group UUID is not correct")

    # -- NETWORK -----------------------------------------------------------------------
    if int(environ.get("FULL_OFFLINE_MODE")) == 0:
        with Session() as chuck:
            # set session options
            chuck.proxies = proxy_settings()
            chuck.verify = bool(int(environ.get("SSL_VERIFICATION", 1)))

            # make requests
            chuck.get("https://api.isogeo.com/about")
            chuck.get("https://id.api.isogeo.com/about")
            chuck.get("https://daemons.isogeo.com/about")
            chuck.get("https://isogeoscan.blob.core.windows.net/")
        logger.info("Network connections are good.")
    else:
        logger.info("Full offline mode enabled: network has not been tested.")

    logger.info("CHECK completed after {:5.2f}s.".format(default_timer() - START_TIME))


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    # additionnal imports
    import multiprocessing

    # workaround for multiprocessing support for packaged version on Windows
    # see: https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    # and: https://stackoverflow.com/a/48805137/2556577
    multiprocessing.freeze_support()
    # launch cli
    check(obj={})
