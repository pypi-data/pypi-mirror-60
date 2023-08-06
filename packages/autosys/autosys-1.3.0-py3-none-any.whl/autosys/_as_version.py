#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
    version.py - Version and Package Information

    Conforms to PEP 566 Metadata for Python Software Packages 2.1
    https://www.python.org/dev/peps/pep-0566/

    - Core metadata specifications
        https://packaging.python.org/specifications/core-metadata/

    - Required fields:
        - Metadata-Version
            * Version of the file format;
            * legal values are “1.0”, “1.1”, “1.2” and “2.1”.

        - Name
            * PEP 508 definition
            * The name of the distribution. The name field is the primary
        identifier for a distribution. A valid name consists only of ASCII
        letters and numbers, period, underscore and hyphen. It must start
        and end with a letter or number. Distribution names are limited to
        those which match the following regex (run with re.IGNORECASE):

        RE_PEP508_NAME = '^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$'

        - Version
            A string containing the distribution’s version number.
            This field must be in the format specified in PEP 440.

    - All other fields are optional:
        Platform - A Platform specification describing an operating system
            supported by the distribution which is not listed in the “Operating
            System” Trove classifiers

        Supported-Platform - Binary distributions containing a PKG-INFO file will
            use the Supported-Platform field in their metadata to specify the OS
            and CPU for which the binary distribution was compiled.

        Summary - A one-line summary of what the distribution does.

        Description - A longer description of the distribution.

        Description-Content-Type - A string stating the markup syntax (if any)
            used in the distribution’s description, so that tools can
            intelligently render the description. Historically, this was plain
            text or RST, but Markdown is common (RFC 7763)

            RFC 7763 - https://www.w3.org/Protocols/rfc1341/4_Content-Type.html

            Example:
            Description-Content-Type: text/markdown; charset=UTF-8; variant=GFM

            The type/subtype part has only a few legal values:
                text/plain
                text/x-rst
                text/markdown

            If a Description-Content-Type is not specified, then applications
            should attempt to render it as text/x-rst; charset=UTF-8 and fall
            back to text/plain if it is not valid rst.

        Keywords - A list of additional keywords, separated by commas, to be used
            to assist searching for the distribution in a larger catalog.

        Home-page - A string containing the URL for the distribution’s home page.

        Download-URL - A string containing the URL from which *this version* of
            the distribution can be downloaded.

        Author - A string containing the author’s name at a minimum;
            additional contact information may be provided.

        Author-email - A string containing the author’s e-mail address or a comma
            separated list of author e-mail addresses. It can contain a name and
            e-mail address in the legal forms for a RFC-822 From: header.

            e.g. "C. Schultz" <cschultz@example.com>

        Maintainer - A string containing the maintainer’s name at a minimum;
            additional contact information may be provided.

            Note that this field is intended for use when a project is being
            maintained by someone other than the original author: it should be
            omitted if it is identical to Author.

        Maintainer-email - A string containing the maintainer’s e-mail address
            with the same conditions as Author.

        License - Text indicating the license covering the distribution where the
            license is not a selection from the “License” Trove classifiers. See
            “Classifier” below. This field may also be used to specify a
            particular version of a license which is named via the Classifier
            field, or to indicate a variation or exception to such a license.

        Classifier - Each entry is a string giving a single classification value
            for the distribution. Classifiers are described in PEP 301, and the
            Python Package Index publishes a dynamic list of currently defined
            classifiers. This field may be followed by an environment marker after
            a semicolon.

            Curated list of classifiers: https://pypi.org/classifiers/

        Requires-Dist - Each entry contains a string naming some other distutils
            project required by this distribution.

        Requires-Python - This field specifies the Python version(s) that the
            distribution is guaranteed to be compatible with. Installation tools
            may look at this when picking which version of a project to install.

        Requires-External - Each entry contains a string describing some
            dependency in the system that the distribution is to be used. This
            field is intended to serve as a hint to downstream project maintainers,
            and has no semantics which are meaningful to the distutils
            distribution.

        Project-URL - A string containing a browsable URL for the project and a
            label for it, separated by a comma.

        Provides-Extra - A string containing the name of an optional feature. Must
            be a valid Python identifier. May be used to make a dependency
            conditional on whether the optional feature has been requested.

    Rarely Used:
        Provides-Dist - Each entry contains a string naming a Distutils project
            which is contained within this distribution.
        Obsoletes-Dist - Each entry contains a string describing a distutils
            project’s distribution which this distribution renders obsolete,
            meaning that the two projects should not be installed at the same time.

    - PEP 345 - Metadata for packages is deprecated
    - PEP 566 - Metadata for Python Software Packages 2.1 is used
    """

import os
import sys
from dataclasses import dataclass
import requests
from typing import List

NL = os.linesep


def troves() -> List[str]:
    """ Return updated list of Trove Classifiers from legacy endpoint.

        https://pypi.org/pypi?%3Aaction=list_classifiers
        """
    TROVES_API_URL: str = 'https://pypi.org/pypi?%3Aaction=list_classifiers'
    response: requests.Response = requests.request('GET', TROVES_API_URL)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        return []


TROVES_LIST: List[str] = troves()
TROVES_STR: str = NL.join(TROVES_LIST)

name: str = __file__.split("/")[-2]
__version__: str = ''
__version__ = '1.1.0'
version: str = __version__
# VERSION = tuple(map(int, __version__.split('.')))
VERSION = __version__
# __version_info__ = tuple(map(int, __version__.split('.')))
__license__: str = "MIT <https://opensource.org/licenses/MIT>"
__author__: str = "Michael Treanor <https://www.github.com/skeptycal>"

# metadata = {
#     'metadata-version': '2.1',
#     'name': name,
#     'version': __version__,
#     'platform': '',
#     'supported_platform': '',
#     'summary': 'System utilities for Python on macOS',
#     'description': open("README.md").read(),
#     'description_content_type': '',
#     'keywords': 'system, cli, macOS, python, utility, developer',
#     'home_page': 'http://github.com/skeptycal/autosys/',
#     'download_url': '',
#     'author': 'Michael Treanor',
#     'author_email': 'skeptycal@gmail.com',
#     'maintainer': '',
#     'maintainer_email': '',
#     'license': '',  # 'only if not in classifiers'
#     'classifier': '',
#     'requires_dist': '',
#     'requires_python': '',
#     'requires_external': '',
#     'project_url': 'http://github.com/skeptycal/autosys/',
#     'provides_extra': '',
# }


# def _debug_info_():
#     if _SET_DEBUG:
#         # ! debug information
#         file_str = f'...{__file__[-20:]:>20.20}'
#         print(f"Debug info for ...{file_str}")
#         print()
#         print(f"{name=}")
#         print(f"{__name__=}")
#         print(f"__file__='{file_str}'")
#         print(f"{__package__=}")
#         print(f"{__license__=}")
#         print(f"{__author__=}")
#         print(f"{__version__=}")
#         print(f"{__version_info__=}")
#         print(f"{VERSION=}")


def main(*args, **kwargs):
    '''
    CLI script main entry point.
    '''
    pass
    # for arg, value in kwargs.items():
    #     if _SET_DEBUG:
    #         print(f'arg: {arg}={value}')
    #     if arg == 'debug' and value == True:
    #         _debug_info_()


if __name__ == "__main__":  # if script is loaded directly from CLI
    _SET_DEBUG: bool = False  # ! set True for dev debugging
    # main(sys.argv[1:], debug=_SET_DEBUG)
    # print(__doc__)
