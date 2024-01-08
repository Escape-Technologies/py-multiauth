# ruff: noqa:T201

"""Multiauth CLI."""

from datetime import date

import pkg_resources

from multiauth.cli.commands.init import init_command
from multiauth.cli.commands.lint import lint_command
from multiauth.cli.commands.parser import build_parser
from multiauth.cli.commands.validate import validate_command

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
    """,
    )

    print('    Maintainer   https://escape.tech')
    print('    Blog         https://escape.tech/blog')
    print('    Contribute   https://github.com/Escape-Technologies/py-multiauth')
    print('')
    print(f'   (c) 2021 - { date.today().year } Escape Technologies - Version: {__version__}')
    print('\n' * 2)

    parser = build_parser()

    args = parser.parse_args()

    match args.command:
        case 'init':
            init_command(args)

        case 'lint':
            lint_command(args)

        case 'validate':
            validate_command(args)


if __name__ == '__main__':
    cli()
