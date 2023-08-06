# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo Scan - Model of metadata output of Sign vector.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint
from typing import Union

# other model


# #############################################################################
# ########## Classes ###############
# ##################################
class Sign(object):
    """Output from FME scripts sign-*."""

    ATTR_TYPES = {
        "error": list,
        "signatures": Union[str, list],
    }

    def __init__(
        self, error: list = None, signatures: Union[str, list] = None,
    ):
        # default values for the object error/properties
        self._error = None
        self._signatures = None

        # if values have been passed, so use them as objects error.
        # error are prefixed by an underscore '_'
        if error is not None:
            self._error = error
        if signatures is not None:
            self._signatures = signatures

    # -- PROPERTIES --------------------------------------------------------------------
    # error
    @property
    def error(self) -> int:
        """Gets the error of this Metadata search.

        :return: The error of this Metadata search.
        :rtype: int
        """
        return self._error

    @error.setter
    def error(self, error: int):
        """Sets the error of this Metadata search.

        :param int error: The error of this Metadata search.
        """

        self._error = error

    # signatures
    @property
    def signatures(self) -> dict:
        """Gets the signatures of this Metadata.

        :return: The signatures of this Metadata.
        :rtype: dict
        """
        return self._signatures

    @signatures.setter
    def signatures(self, signatures: dict):
        """Sets the coordinate systems of this Metadata.

        :param dict signatures: to be set
        """

        self._signatures = signatures

    # -- METHODS -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Returns the model properties as a dict."""
        result = {}

        for attr, _ in self.ATTR_TYPES.items():
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict")
                        else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(Sign, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self) -> str:
        """Returns the string representation of the model."""
        return pprint.pformat(self.to_dict())

    def __repr__(self) -> str:
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other) -> bool:
        """Returns true if both objects are equal."""
        if not isinstance(other, Sign):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other) -> bool:
        """Returns true if both objects are not equal."""
        return not self == other


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    sample = Sign()
