"""
https://realpython.com/command-line-interfaces-python-argparse/#setting-the-name-of-the-program
"""

import argparse
from pique.themes import THEMES

__all__ = ['parser']

parser = argparse.ArgumentParser(
    prog='pq',
    description='Pique: Query and transform JSON data on the command line',
    epilog=(
        'If this tool is useful to you please give it a star on GitHub: '
        'https://github.com/Pebaz/pique'
    )
)

parser.add_argument(
    'query',
    nargs='?',
    default='',
    help='transform and select data from JSON input'
)

parser.add_argument(
    '--nocolor',
    action='store_false',
    help='do not syntax highlight JSON output'
)

parser.add_argument(
    '--theme',
    help='syntax theme for JSON output',
    choices=[i.__name__ for i in THEMES]
)

parser.add_argument(
    '--fullhelp',
    action='store_true',
    help='show query syntax tutorial'
)

parser.add_argument(
    '--debug',
    action='store_true',
    help='show parsed queries and other debug info'
)
