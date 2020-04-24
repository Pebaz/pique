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
'(a.b.c).(lm().nop()).().[-1].[*].[1:-1].{foo}.{foo,bar}.{"whoa" : {"name":"Pebaz"}}.{foo : 123, bar}.name.person\.age.`|^^%$#`'




         Fanout    Join
           |        |
           V        V
Functions.[*].Name.[!].(len(IT))






"""


# NOTE: CREATE AN assign() FUNCTION THAT CAN ASSIGN WITHIN AN EXPRESSION

import sys, json, ast, types


class BetterNamespace(types.SimpleNamespace):
    def __getitem__(self, key):
        return getattr(self, key)


class Query:
    "Base class for all queries"
    def __init__(self, source):
        self.source = source

    def __call__(self, data, queries):
        return data

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<{self.__class__.__name__}: {repr(self.source)}>'
        

class SelectKey(Query):  # some-key | `some-key` | some key
    "Narrow down data"

    def __call__(self, data, queries):
        if (
            self.source not in data and
            isinstance(self.source, str) and
            self.source.lstrip('+-').isdigit()
        ):
            raise TypeError(
                f'Cannot index object with int: {self.source}. '
                f'Use array syntax instead: [{self.source}]'
            )
        else:
            try:
                return data[self.source]
            except Exception as e:
                print(e)
                print('Source:', self.source)
                print('queries:', queries)
                print('data:', data)
                sys.exit()
            

class BuildObject(Query):  # {}
    "Filter or enhance data"


class Index(Query):  # []
    "Index an object or an array"

    def __init__(self, source):
        Query.__init__(self, source)
        if ':' in source:
            self.index = slice(*map(int, source.split(':')))
        elif source in '*!':
            self.index = source
        else:
            self.index = int(source)
    
    def __call__(self, data, queries):
        if self.index == '*':
            print('*' * 30)
            print(queries)
            print('*' * 30)
            # Syntax cannot handle: [*].name and return a list of names.
            # TODO(pebaz): Eval everything in the returned list using the rest
            # of the queries in `process_queries`
            return [process_queries(i, queries) for i in data]
            #return [i for i in data]

        elif self.index == '!':
            return data

        else:
            return data[self.index]


class Expression(Query):  # ()
    "Query an object using a Python expression"

    def __call__(self, data, queries):

        env = (
            {name : value for name, value in data.items()}
            if isinstance(data, dict) else {}
        )

        env.update({
            'IT' : data

            # TODO(pebaz): MAP EVERY SINGLE BUILTIN METHOD SUCH AS __int__ TO
            # BETTERNAMESPACE AND HAVE A __to_dict__() METHOD THAT RETURNS A
            # COPY OF THE ORIGINAL JSON GIVEN AT TIME OF CREATION.
            #'IT' : BetterNamespace(**data),
            #'assign' : lambda x, y: print(x, y)
            # 'keys' : lambda x: x.keys()
        })

        data = eval(self.source, env)

        if isinstance(data, BetterNamespace):
            data = data.__dict__

        return data


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
                commands.append(Expression(buffer.strip()))
                buffer = ''
                state = DOT
            else:
                buffer += i

        elif state == SQUARE:
            stripped = buffer.strip()
            if i == ']':
                if (is_valid_python_code(stripped) or stripped in '*!'):
                    commands.append(Index(stripped))
                    buffer = ''
                    state = DOT
                elif ':' in stripped:
                    try:
                        commands.append(Index(stripped))
                        buffer = ''
                        state = DOT
                    except:
                        raise SyntaxError(stripped)
                else:
                    raise SyntaxError(stripped)
            else:
                buffer += i

        elif state == BRACE:
            if i in '},:' and is_valid_python_code(buffer.strip()):
                brace_key_list.append(buffer.strip())
                buffer = ''
                if i == ':':
                    brace_key_list.append(':')
                elif i == '}':
                    commands.append(BuildObject(brace_key_list[:]))
                    brace_key_list.clear()
                    state = DOT
            else:
                buffer += i

        elif state == KEY:
            if i == '\\':
                buffer += next(query_it)
            elif i == '.':
                commands.append(SelectKey(buffer))
                buffer = ''
                state = DOT
            else:
                buffer += i

    # It is possible to be in the KEY state after loop exit
    if state == KEY:
        commands.append(SelectKey(buffer))

    elif state == DOT:
        "That's ok too"

    # But not any other state
    else:
        raise SyntaxError(
            f'Failed to finish parsing {state} - Incomplete query:\n\n'
            f'    {query}\n'
            f'    {" " * (len(query) - len(buffer))}^\n'
            f'    {" " * (len(query) - len(buffer))}|\n'
        )

    return commands


def process_queries2(data: dict, queries: list) -> dict:
    "Performs a list of queries on JSON data."

    print(data)

    fanout = False

    index = 0
    for i in range(len(queries)):
        query = queries[index]

        if isinstance(query, Index):
            if query.source == '*':
                fanout = True
                data = query(data, queries[index + 1:])
                while index < len(queries) and isinstance(query, Index) and query.source != '!':
                    index += 1
                if index == len(queries):
                    return data

            elif query.source == '!':
                fanout = False
                index += 1
                continue


        if not fanout: data = query(data, queries[2:])

        index += 1

    return data


def process_queries(data, queries):
    fanout = 0

    for i in range(len(queries)):
        query = queries[i]

        if fanout:
            print(fanout, i)
            if i == fanout:
                fanout = 0
            else:
                fanout -= 1
                continue

        if isinstance(query, Index) and query.source == '*':
            q = []
            for j in range(i + 1, len(queries) - 1):
                if isinstance(queries[j], Index) and queries[j].source == '!':
                    break
                q.append(queries[i])
            print('Queries:', q)
            data = query(data, q)
            #fanout = j + add

        else:
            data = query(data, queries)

    return data


def is_valid_python_code(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def output_highlighted_json(json_data, color=True, theme: str=None):
    "Print highlighted JSON to the console except when in a pipe."

    formatted_json = json.dumps(json_data, indent=4)

    # If in pipe, don't print console colors, just print text
    if color and sys.stdout.isatty():
        if sys.platform == 'win32':
            import colorama
            colorama.init()

        from pygments import highlight
        from pygments.lexers import JsonLexer
        from pygments.formatters import Terminal256Formatter
        from pique import themes

        theme_list = themes.__dict__
        theme = theme or 'Python3'

        if (theme not in theme_list or
            not issubclass(theme_list[theme], themes.Style)
        ):
            raise Exception(f'No theme named: {theme}')

        color_theme = theme_list[theme]

        formatted_json = highlight(
            formatted_json,
            JsonLexer(),
            Terminal256Formatter(style=color_theme)
        )

    print(formatted_json)


def main(args: list=[]) -> int:
    "Run pq to query JSON data from CLI"

    from pique.cli import parser

    # if len(sys.argv) == 1 and sys.stdin.isatty():
    #     parser.print_help()
    #     return 0

    # elif sys.stdin.isatty():
    #     print('No JSON data to read from pipe. Exiting.')
    #     return 0

    cli = parser.parse_args(args or sys.argv[1:])

    try:
        commands = parse_query_string(cli.query)
    except SyntaxError as e:
        print(f'{e.__class__.__name__}: {e}')
        return 1

    json_data = json.loads(open('fanout.json').read())

    # try:
    #     json_data = json.loads(sys.stdin.read())
    # except json.JSONDecodeError:
    #     print('Error reading JSON data. Is it formatted properly and complete?')
    #     return 1

    # if cli.debug:
    print('---------------------')
    print(cli.query, '\n')
    print('[')
    for c in commands:
        print('   ', c)
    print(']')

    # try:
    json_data = process_queries(json_data, commands)
    # except Exception as e:
    #     print(f'{e.__class__.__name__}: {e}')
    #     return 1

    output_highlighted_json(json_data, cli.nocolor, cli.theme)

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        pass
