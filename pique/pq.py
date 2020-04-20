"""
logGroups.[*].(name in [1, 2, 3])
logGroups.[*].{logGroupName,storedBytes}.(storedBytes > 1000000)
logGroups.[*].(storedBytes > 1000000).{logGroupName,storedBytes}
Things.[*].{foo,bar,baz:'chuzzle'}.(bar in 1, 2, 3)

sum()

builtin_func3()

logGroups.(sort(IT))

People.(len(IT)) ->
12


# -----------
# THIS IS WRONG:
Person.(len(IT.name)) ->
23

# IT SHOULD BE:
Person.(len(name)) ->
23
# Because the `IT` should only be used for the toplevel object, not keys
Person.Contacts.(sort(IT))

# -----------

{"name" : "Pebaz"}
Person.(assign(name, name * 2)) ->  ALSO: Person.{"name" : name * 2}
    <- "name" is there because `name` is bound to the object key
{
    "name": "PebazPebaz"
}

[1, 2, 3, 4]
Array.(len(IT)) ->
4

[1, 2, 3, 4]
Array.{"len" : len(IT)} ->
{
    "len": 4
}

Support Slice Objects:
Array.foo.[1:-3:2]

someobject[slice(*("[1:-3:2]".split(':')))]


[integer] (Python) {Python, Pyhon : Python}

( print( "))))" ) ).this.[0].not.valid.python.{}
"""


# NOTE: CREATE AN assign() FUNCTION THAT CAN ASSIGN WITHIN AN EXPRESSION
# NOTE: USE A STDLIB FUNCTION TO PARSE EXPRESSIONS FOR PROPER SYNTAX.
# NOTE: DON'T USE A STATE MACHINE. MAKE PASSES FOR EACH PAREN COMBO
# NOTE: IF YOU COME TO A DOT AND THE PAREN IS MATCHED, ITS DONE.

import sys, json, ast
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


def is_valid_python_code(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def main(args):
    query = '( print( "))))".strip() ) )' #.this.[0].not.valid.python.{}'
    query = '(a.b.c)'

    print('Input string:', repr(query))
    
    paren = ''

    for i in query[1:]:  # We are forcing a PAREN state right now
        if i == ')':
            if is_valid_python_code(paren.strip()):
                paren = paren.strip()  # Whitespace could be part of a string
                print(paren)  # Switch to the next state.
            else:
                paren += i
        else:
            paren += i


    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

