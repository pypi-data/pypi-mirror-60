# -----------------------------------------------------------------------------
#
# This file is the copyrighted property of Tableau Software and is protected
# by registered patents and other applicable U.S. and international laws and
# regulations.
#
# Unlicensed use of the contents of this file is prohibited. Please refer to
# the NOTICES.txt file for further details.
#
# -----------------------------------------------------------------------------
from typing import Optional


class HyperException(Exception):
    """
    An exception raised by the Hyper API.
    Note that error messages may change in the future versions of the library.
    """

    message: Optional[str]
    hint_message: Optional[str]
    context_id: int

    def __init__(
            self,
            context_id: int,
            message: Optional[str] = None,
            hint_message: Optional[str] = None):
        super().__init__(context_id, message, hint_message)

        self.message = message
        self.context_id = context_id
        self.hint_message = hint_message

    def __str__(self):
        """
        Returns the default string representation of this exception.

        The string is in the format ``<context>: <message>``.
        """
        s = ""
        if self.message:
            s += self.message.replace("\n", "\n\t")

        if self.hint_message:
            s += "\nHint: " + self.hint_message.replace("\n", "\n\t")

        s += "\nContext: " + hex(self.context_id & (2**32 - 1))

        if self.__cause__ is not None:
            s += "\n\nCaused by:\n"
            s += str(self.__cause__)

        return s


# noinspection PyPep8Naming
def ContextId(id: int):  # noqa
    """
    Tag an integer as a context id.

    Each throw clause has a unique context id that is stored in the thrown error.
    """
    return id
