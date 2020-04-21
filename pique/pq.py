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
    def __init__(self, source):
        self.source = source

    def __str__(self):
        return f'<{self.__class__.__name__}: {repr(self.source)}>'
        
class SelectKey(Query):  # some-key | `some-key` | some key
    "Narrow down data"

class BuildObject(Query):  # {}
    "Filter or enhance data"

class Index(Query):  # []
    "Index an object or an array"

    def __init__(self, source):
        Query.__init__(self, source)
        if ':' in source:
            index = slice(*map(int, source.split(':')))
        elif source == '*':
            index = source
        else:
            index = int(source)

class Expression(Query):  # ()
    "Query an object using a Python expression"


def parse_query_string(query: str) -> list:
    "Parses out each query string into its own string"

    DOT, PAREN, SQUARE, BRACE, KEY = 'DOT PAREN SQUARE BRACE KEY'.split()
    commands = []
    state = DOT
    buffer = ''
    brace_key_list = []
    query_it = iter(query)

    for i in query_it:
        if state == DOT:
            if i == '.':
                continue
            elif i == '(':
                state = PAREN
            elif i == '[':
                state = SQUARE
            elif i == '{':
                state = BRACE
            else:
                buffer += i
                state = KEY

        elif state == PAREN:
            if i == ')' and is_valid_python_code(buffer.strip()):
                #commands.append(f'<PAREN: {repr(buffer.strip())}>')
                commands.append(Expression(buffer.strip()))
                buffer = ''
                state = DOT
            else:
                buffer += i

        elif state == SQUARE:
            stripped = buffer.strip()
            if i == ']':
                if (is_valid_python_code(stripped) or stripped == '*'):
                    #commands.append(f'<SQUARE: {repr(stripped)}>')
                    commands.append(Index(stripped))
                    buffer = ''
                    state = DOT
                elif ':' in stripped:
                    try:
                        #commands.append(f'<SQUARE: {repr(stripped)}>')
                        commands.append(Index(stripped))
                        buffer = ''
                        state = DOT
                    except:
                        raise Exception('Invalid Syntax')
                else:
                    raise Exception('Invalid Syntax')
            else:
                buffer += i

        elif state == BRACE:
            if i in '},:' and is_valid_python_code(buffer.strip()):
                brace_key_list.append(buffer.strip())
                buffer = ''
                if i == ':':
                    brace_key_list.append(':')
                elif i == '}':
                    #commands.append(f'<BRACE: {repr(brace_key_list)}>')
                    commands.append(BuildObject(brace_key_list[:]))
                    brace_key_list.clear()
                    state = DOT
            else:
                buffer += i

        elif state == KEY:
            if i == '\\':
                buffer += next(query_it)
            elif i == '.':
                #commands.append(f'<KEY: {repr(buffer)}>')
                commands.append(SelectKey(buffer))
                buffer = ''
                state = DOT
            else:
                buffer += i

    # It is possible to be in the KEY state after loop exit
    if state == KEY:
        #commands.append(f'<KEY: {repr(buffer)}>')
        commands.append(SelectKey(buffer))

    return commands


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
    query = ''.join(sys.argv[1:]) or '(a.b.c).(lm().nop()).().[-1].[*].[1:-1].{foo}.{foo,bar}.{"whoa" : {"name":"Pebaz"}}.{foo : 123, bar}.name.person\.age.`|^^%$#`'

    print('---------------------')
    print(query)

    commands = parse_query_string(query)

    print()
    print('[')
    for c in commands:
        print('   ', c)
    print(']')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

