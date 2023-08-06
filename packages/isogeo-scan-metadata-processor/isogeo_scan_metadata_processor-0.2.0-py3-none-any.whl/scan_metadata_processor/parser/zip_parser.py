# coding: utf-8
#! python3  # noqa: E265

"""
    Manipulate zipped files.

    See:

    - https://docs.python.org/fr/3/library/zipfile.html

"""


# #############################################################################
# ########## Libraries #############
# ##################################
# standard library
import logging
from os import access, R_OK
from pathlib import Path
from typing import Union
from zipfile import BadZipFile, is_zipfile, ZipFile

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ##############################################################################
# ########## Classes ###############
# ##################################
class Unzipper:
    """Check and extract files from a zip archive.

    :param zip_path: path to the zip file to unzip.
    """

    def __init__(self, zip_path: Union[str, Path]):
        """Instanciating Unzipper."""
        self.zipfile_path = self.check_zip(zip_path)

    def check_zip(self, zip_path: Union[str, Path]) -> Path:
        """Perform some checks on passed zip file and load it as Path object.

        :param zip_path: path to the zip file to unzip.

        :returns: sanitized zip path
        :rtype: Path
        """
        # if path as string load it in Path object
        if isinstance(zip_path, str):
            try:
                zip_path = Path(zip_path)
            except Exception as exc:
                raise TypeError("Converting zip path failed: {}".format(exc))

        # check if file exists
        if not zip_path.exists():
            raise FileExistsError(
                "Zipfile to check doesn't exist: {}".format(zip_path.resolve())
            )

        # check if it's a file
        if not zip_path.is_file():
            raise IOError("Zipfile is not a file: {}".format(zip_path.resolve()))

        # check if file is readable
        if not access(zip_path, R_OK):
            raise IOError("Zip file isn't readable: {}".format(zip_path))

        # check if file is a zip
        if not is_zipfile(zip_path):
            raise BadZipFile("File isn't a ZIP: {}".format(zip_path))

        # check integrity
        try:
            with ZipFile(file=zip_path) as in_zip:
                in_zip.testzip()
        except BadZipFile as exc:
            raise exc

        # return sanitized path
        return zip_path

    def unzip(
        self,
        to_folder: Union[str, Path],
        all_in: bool = True,
        only_extensions: tuple = None,
    ) -> list:
        """Extract files from zip. Can extract every files or filter on some extensions.

        :param to_folder: path to the output folder. If it doesn't exist, it'll be created.
        :param all_in: option to extract all files. Default: True.
        :param only_extensions: option to filter on certain extensions. Default: None.

        Raises:
            PermissionError: if output folder is not writable

        :returns: list of extracted files
        :example:

        .. code-block:: python

            for i in fixtures_dir.glob("**/*.zip"):
                unzipper = Unzipper(i)
                print(unzipper.zipfile_path)

                # extract all files
                unzipper.unzip(fixtures_dir / "unzipper/all_in", all_in=1)

                # extract only JSON
                unzipper.unzip(
                    to_folder=Path(fixtures_dir / "unzipper/filtered"),
                    all_in=0,
                    only_extensions=(".json",),
                )

        """
        # check args conflicts
        if all_in and only_extensions is not None:
            logger.warning(
                "'all_in' and 'only_extension' are exclusive: "
                "if the first is True, then the second must be None. "
                "The option only_extension will be kept."
            )
            all_in = False
        elif not all_in and only_extensions is None:
            logger.warning(
                "'all_in' and 'only_extension' are exclusive: "
                "if the first is False, then the second must be a tuple. "
                "The option 'all_in' will be set to True."
            )
            all_in = True

        # ensure the the output folder is created
        try:
            to_folder.mkdir(exist_ok=True, parents=True)
        except PermissionError:
            raise PermissionError(
                "Output folder is not writable: {}".format(to_folder.resolve())
            )

        if not to_folder.is_dir():
            logger.warning(
                "Passed output path is not a folder: {}. Parent folder will be used instead.".format(
                    to_folder.resolve()
                )
            )
            to_folder = to_folder.parent

        # option to extract everything
        if all_in and only_extensions is None:
            with ZipFile(file=self.zipfile_path) as in_zip:
                in_zip.extractall(to_folder)
            logger.info(
                "{} files extracted to {} from {}".format(
                    len(in_zip.namelist()),
                    to_folder.resolve(),
                    self.zipfile_path.resolve(),
                )
            )
            # return with extracted files list
            return in_zip.namelist()

        # option to extract only certain files
        if not all_in and isinstance(only_extensions, tuple):
            li_extracted_files = []
            with ZipFile(file=self.zipfile_path) as in_zip:
                for file_to_extract in in_zip.namelist():
                    if file_to_extract.endswith(only_extensions):
                        in_zip.extract(file_to_extract, to_folder)
                        li_extracted_files.append(file_to_extract)

            # return with extracted files list
            return li_extracted_files


# #############################################################################
# ##### Main #######################
# ##################################
if __name__ == "__main__":
    pass
