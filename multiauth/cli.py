"""Multiauth CLI."""

from datetime import date

import pkg_resources

from multiauth.main import MultiAuth

__version__ = pkg_resources.get_distribution('py-multiauth').version


# pylint: disable=trailing-whitespace
def cli() -> None:
    """Entry point of the CLI program."""

    print(
        r"""
__________          _____        .__   __  .__   _____          __  .__     
\______   \___.__. /     \  __ __|  |_/  |_|__| /  _  \  __ ___/  |_|  |__  
 |     ___<   |  |/  \ /  \|  |  \  |\   __\  |/  /_\  \|  |  \   __\  |  \ 
 |    |    \___  /    Y    \  |  /  |_|  | |  /    |    \  |  /|  | |   Y  \
 |____|    / ____\____|__  /____/|____/__| |__\____|__  /____/ |__| |___|  /
           \/            \/                           \/                 \/                              
    """
    )

    print('    Maintainer   https://escape.tech')
    print('    Blog         https://blog.escape.tech')
    print('    Contribute   https://github.com/Escape-Technologies/py-multiauth')
    print('')
    print(f'   (c) 2021 - { date.today().year } Escape Technologies - Version: {__version__}')
    print('\n' * 2)

    MultiAuth()
