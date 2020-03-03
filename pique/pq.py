"""
"""

import sys, json
from pique.cli import parser

print(parser.parse_args(sys.argv[1:]))
