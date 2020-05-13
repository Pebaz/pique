from pique.pq import *

def test_parser():
    assert parse_query_string('foo.bar.baz') == [
        SelectKey('foo'), SelectKey('bar'), SelectKey('baz')
    ]


def test_form_query_groups():
    queries = parse_query_string('foo.bar.baz')
    assert form_query_groups(queries) == [
        [SelectKey('foo'), SelectKey('bar'), SelectKey('baz')]
    ]


def test_run_query_group():
    query_group = [SelectKey('name')]
    assert run_query_group({'name' : 'Pebaz'}, query_group) == 'Pebaz'


def test_process_queries():
    query_groups = [[SelectKey('name')]]
    assert process_queries({'name' : 'Pebaz'}, query_groups) == 'Pebaz'


def test_is_valid_python_code():
    assert is_valid_python_code('print(1)')
    assert is_valid_python_code('print(i for i in range(10))')
    assert is_valid_python_code('print(\'asdf\', "asdf")')
    assert is_valid_python_code('print(asdf)')
    assert is_valid_python_code('print(...)')
    assert is_valid_python_code('print({"name":"Pebaz"})')
    

def test_pique_as_lib():
    gold1 = {'FuncA', 'FuncB', 'FuncC', 'FuncD'}
    data = {
        'Functions' : [
            {'FunctionName' : i, 'CodeSize' : 1024} for i in gold1
        ]
    }

    for name in query(data, "Functions.[*].FunctionName"):
        assert name in gold1

    assert query(data, "Functions.[*].FunctionName") == list(gold1)
