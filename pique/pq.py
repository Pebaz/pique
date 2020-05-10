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





* Unit Tests
* Dotfile Support
    * JSON indentation
    * Default theme
    * Plugins
* Markdown Docs `docs/`
* Create `release` branch
* GitHub Actions Pipeline
* Fix bugs
    BUG: array.[:-1]
    BUG: {boolean,odd$key?}
"""


# NOTE: CREATE AN assign() FUNCTION THAT CAN ASSIGN WITHIN AN EXPRESSION

import sys, json, ast, types, traceback, pathlib
import importlib.util


DOTFILE = pathlib.Path('~/.pq').expanduser().absolute()
SETTINGS = {}
PLUGINS = {}

if DOTFILE.exists():
    try:
        spec = importlib.util.spec_from_loader(
            'plugins', importlib.machinery.SourceFileLoader('plugins', str(DOTFILE))
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, '__settings__'):
            SETTINGS = module.__settings__
        PLUGINS = {
            key : val for key, val in module.__dict__.items()
            if not key.startswith('__') and not key.endswith('__')
        }
    except Exception as e:
        print('Error loading dotfile:', e)


class Query:
    "Base class for all queries"
    def __init__(self, source):
        self.source = source

    def __call__(self, data):
        return data

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<{self.__class__.__name__}: {repr(self.source)}>'

    def __eq__(self, other):
        return self.source == other.source

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.source)
        

class SelectKey(Query):  # some-key | `some-key` | some key
    "Narrow down data"

    def __call__(self, data):
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
                message = getattr(e, 'message', None)

                if message:
                    print(f'{e.__class__.__name__}: {message}')
                else:
                    print(repr(e))
                sys.exit()
            

class BuildObject(Query):  # {}
    "Filter or enhance data"

    def __init__(self, source):
        Query.__init__(self, source)
        source_queries = source[:]
        indices = []
        
        while len(source_queries) > 2:
            if source_queries[1] == ':':
                key, _, val = [source_queries.pop(0) for i in range(3)]
                indices.append((key, val))
            else:
                indices.append(source_queries.pop(0))

        indices.extend(source_queries)
        self.indices = indices

    def __call__(self, data):
        result = {}
        for query in self.indices:
            if len(query) == 2:
                key, val = query
                result[Expression(key)(data)] = Expression(val)(data)
            else:
                result[query] = Expression(query)(data)
        return result


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
    
    def __call__(self, data):
        return data[self.index]


class Expression(Query):  # ()
    "Query an object using a Python expression"

    def __call__(self, data):
        env = (
            {name : value for name, value in data.items()}
            if isinstance(data, dict) else {}
        )
        env.update(PLUGINS)
        env.update(IT=data)
        data = eval(self.source, env)
        return data


class Fanout(Query):  # [*]
    "Process each element in the current item with the next query set."


class Select(Query):  # [-]
    "Remove any value from array that doesn't evaluate to True"


class Join(Query):  # [!]
    "Join a previously entered Fanout command into a List."


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
                if (is_valid_python_code(stripped) or stripped in '*!-'):
                    if stripped == '*':
                        commands.append(Fanout(stripped))
                    elif stripped == '!':
                        commands.append(Join(stripped))
                    elif stripped == '-':
                        commands.append(Select(stripped))
                    else:
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


def form_query_groups(queries):
    groups, group = [[]], 0

    for query in queries:
        if isinstance(query, (Fanout, Join, Select)):
            groups.extend([query, []])

        else:
            groups[-1].append(query)

    return groups


def run_query_group(data, queries):
    for query in queries:
        data = query(data)
    return data


def process_queries(data, groups):
    groups_it = iter(groups)

    for group in groups_it:
        if isinstance(group, Fanout):
            next_group = next(groups_it)
            data = [run_query_group(item, next_group) for item in data]
            continue

        elif isinstance(group, Join):
            data = run_query_group(data, next(groups_it))
            continue

        elif isinstance(group, Select):
            next_group, result = next(groups_it), []
            data = [item for item in data if run_query_group(item, next_group)]
            continue
        
        else:
            data = run_query_group(data, group)

    return data


def is_valid_python_code(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def output_highlighted_json(json_data, color=True, theme: str=None):
    "Print highlighted JSON to the console except when in a pipe."

    formatted_json = json.dumps(json_data, indent=SETTINGS.get('indent', 4))

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

    if len(sys.argv) == 1 and sys.stdin.isatty():
        parser.print_help()
        return 0

    elif sys.stdin.isatty():
        print('No JSON data to read from pipe. Exiting.')
        return 0

    cli = parser.parse_args(args or sys.argv[1:])

    try:
        commands = parse_query_string(cli.query)
    except SyntaxError as e:
        print(f'{e.__class__.__name__}: {e}')
        return 1

    try:
        json_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print('Error reading JSON data. Is it formatted properly and complete?')
        return 1

    if cli.debug:
        print('---------------------')
        print(' Query string:\n')
        print('    ', cli.query, '\n')
        print('[')
        for c in commands:
            print('   ', c)
        print(']\n')
        print('Output:\n')

    try:
        json_data = process_queries(json_data, form_query_groups(commands))
    except Exception as e:
        if cli.debug:
            traceback.print_exc()
        else:
            print(f'{e.__class__.__name__}: {e}')
        return 1

    # NOTE(pebaz): `theme` can be None. `output_highlighted_json` uses Python3.
    theme = cli.theme or SETTINGS.get('theme')

    output_highlighted_json(json_data, cli.nocolor, theme)

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        pass
