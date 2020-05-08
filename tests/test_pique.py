from pique.pq import *

def test_parser():
    assert parse_query_string('foo.bar.baz') == [SelectKey('foo'), SelectKey('bar'), SelectKey('baz')]
