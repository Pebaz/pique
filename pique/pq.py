"""
"""

# NOTE: CREATE AN assign() FUNCTION THAT CAN ASSIGN WITHIN AN EXPRESSION
# NOTE: USE A STDLIB FUNCTION TO PARSE EXPRESSIONS FOR PROPER SYNTAX.

import sys, json
from pique.cli import parser


class Query:
    "Base class for all queries"

class SelectKey(Query):
    "Narrow down data"

class BuildObject(Query):
    "Filter or enhance data"

class Index(Query):
    "Index an object or an array"

class Expression(Query):
    "Query an object using a Python expression"


def parse_query_string(query_string: str) -> list:
    "Parses out each query string into its own string"

    # "logGroups.[*].(storedBytes.foo.bar > 1000000).{logGroupName,storedBytes}"

    print()
    print(query_string)
    print()

    query_string += '.'

    def choose_state(char):
        state_map = {
            '[' : 'index',
            '{' : 'build',
            '(' : 'query'
        }
        if char in state_map:
            return state_map[char]
        else:
            return 'select'

    state = choose_state(query_string[0])
    stack = []
    groups = []
    active_brace = False
    index = 0

    opposite = {
        '[' : ']',
        '(' : ')',
        '{' : '}',
        ']' : '[',
        '}' : '{',
        ')' : '('
    }

    for i in range(1, len(query_string)):
        char = query_string[i]

        # Handle EOL and group submission, regardless of state
        if char == '.' and not stack:
            groups.append(query_string[index:i])
            index = i + 1
            if i < len(query_string) - 1:
                state = choose_state(query_string[i + 1])
            continue

        elif char in '[{(':
            # First ever brace
            if not stack:
                # May be able to change to: stack = ['(', ')']
                stack.append(char)

            # Matching brace
            elif stack[-1] == opposite[char]:
                stack.append(char)

            else:
                pass

        elif char in ']})':
            if stack[-1] in '[{(':
                stack.pop()

            elif stack[-1] == opposite[char]:
                stack.pop()

            else:
                pass

    if stack:
        "Something went wrong..."

    return groups


def build_query(query_list: list) -> list:
    "Build a list of queries to run on a given data set"
    return []


def query(data: dict, query_string: str) -> dict:
    """
    """


def main(args: list=[]) -> int:
    "Run pq to query JSON data from CLI"
    args = args or sys.argv[1:]

    cli = parser.parse_args(args)

    print(cli)
    print(parse_query_string(cli.query))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

