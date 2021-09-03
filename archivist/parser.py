"""common parser argument
"""

# pylint:  disable=missing-docstring
# pylint:  disable=too-few-public-methods


import argparse
from enum import Enum
import logging
from sys import exit as sys_exit

from .archivist import Archivist
from .logger import set_logger
from .storage_integrity import StorageIntegrity

LOGGER = logging.getLogger(__name__)


# from https://stackoverflow.com/questions/43968006/support-for-enum-arguments-in-argparse
class EnumAction(argparse.Action):
    """
    Argparse action for handling Enums
    """

    def __init__(self, **kwargs):
        # Pop off the type value
        enum_type = kwargs.pop("type", None)

        # Ensure an Enum subclass is provided
        if enum_type is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")

        if not issubclass(enum_type, Enum):
            raise TypeError("type must be an Enum when using EnumAction")

        # Generate choices from the Enum
        kwargs.setdefault("choices", tuple(e.name for e in enum_type))

        super().__init__(**kwargs)

        self._enum = enum_type

    def __call__(self, parser, namespace, values, option_string=None):
        # Convert value back into an Enum
        value = self._enum[values]
        setattr(namespace, self.dest, value)


def common_parser(description):
    """Construct parser with security option for token/auth authentication"""
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="print verbose debugging",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        dest="url",
        action="store",
        default="https://rkvst.poc.jitsuin.io",
        help="location of Archivist service",
    )
    parser.add_argument(
        "-i",
        "--storage-integrity",
        type=StorageIntegrity,
        action=EnumAction,
        dest="storage_integrity",
        default=StorageIntegrity.TENANT_STORAGE,
        help="Assets will be created on the ledger or on tenant storage",
    )

    security = parser.add_mutually_exclusive_group(required=True)
    security.add_argument(
        "-t",
        "--auth-token",
        type=str,
        dest="auth_token_file",
        action="store",
        default=".auth_token",
        help="FILE containing API authentication token",
    )
    security.add_argument(
        "-c",
        "--clientcert",
        type=str,
        dest="client_cert_name",
        action="store",
        help=(
            "name of TLS client cert (.key and .pem with matching name must"
            "be in current directory)"
        ),
    )

    return parser, security


def endpoint(args):

    if args.verbose:
        set_logger("DEBUG")
    else:
        set_logger("INFO")

    LOGGER.info("Initialising connection to Jitsuin Archivist...")
    fixtures = {
        "assets": {
            "storage_integrity": args.storage_integrity.name,
        },
    }

    if args.auth_token_file:
        with open(args.auth_token_file, mode="r") as tokenfile:
            authtoken = tokenfile.read().strip()

        arch = Archivist(args.url, auth=authtoken, verify=False, fixtures=fixtures)

    elif args.client_cert_name:
        arch = Archivist(
            args.url, cert=args.client_cert_name, verify=False, fixtures=fixtures
        )

    if arch is None:
        LOGGER.error("Critical error.  Aborting.")
        sys_exit(1)

    return arch
