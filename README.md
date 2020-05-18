# Pique

> Query JSON from the CLI using Python syntax

## What is Pique

Pique is a command line JSON query and processing tool similar to
[JQ](https://stedolan.github.io/jq/) and [JMESPath](https://jmespath.org/).

However, while these other applications are highly useful, they introduce yet
another query language to learn. With Pique, you can use any valid Python
expression in your queries, bringing the full power of Python expressions to
your CLI.

It should be noted that Pique does not have a complete specification like
[JMESPath](https://jmespath.org/specification.html) because Pique's main feature
is to allow you to use Python expressions within queries whereas JMESPath is a
query language that can be implemented in any language and imported as a
library.

Pique is great for:

 * Examine content of JSON documents beyond simple text output/processing
 * Query the results returned from AWS CLI commands using Python expressions

## Installation

```bash
$ pip install python-pique
```

Pique works on:

* Windows
* MacOS
* Linux
* Any platform that Python3 runs on

## Usage

```bash
$ cat example.json | pq

$ echo '{ "name" : "Pebaz" }' | pq name  # "Pebaz"
```

## Tutorial

To query JSON using Pique, you can use a query string provided on the command
line. A query string is comprised of 4 unique query syntax types that are very
similar to their Python equivalents:

 * Key selection: `any characters between the dot . characters`
 * Brackets: `[]`
 * Braces: `{}`
 * Parentheses: `()`

You can form sequences of these queries by separating them by a dot `.`
character. For instance, the following is an example query that results in the string:
"foo".

```bash
$ cat foo.json
{
    "obj" : {
        "arr" : [
            "baz", "bar", "foo"
        ]
    }
}

$ cat foo.json | pq 'obj.arr.[2]'
"foo"
```

In between each dot `.` character you can place any of these query types:

 * [SelectKey](#SelectKey-key1.key2.key3): `keyname`
 * [Index](#Index-4): `[123]`
 * [BuildObject](#BuildObject-name,age): `{name,age,"address":address.upper(),phone}`
 * [Expression](#Expression-sorted(IT)): `(i for i in range(10))`
 * [Fanout](#Fanout-*-&-Join): `[*]`
 * [Join](#Fanout-*-&-Join): `[!]`
 * [Select](#Select): `[-]`

### SelectKey `key1.key2.key3`

The SelectKey query is the most basic type of query. It allows you to drilldown
on a given JSON structure and can be used to restrict the data that the next
query in the sequence can work with.

### Index `[4]`

You can use the Index query to index JSON arrays. Within the brackes, you can
put any valid Python slice. Here are a few examples:

```python
$ echo '[1, 2, 3, 4, 5]' | pq '[0]'
1
$ echo '[1, 2, 3, 4, 5]' | pq '[-1]'
5
$ echo '[1, 2, 3, 4, 5]' | pq '[2:4]'
[3, 4]
$ echo '[1, 2, 3, 4, 5]' | pq '[::2]'
[1, 3, 5]
$ echo '[1, 2, 3, 4, 5]' | pq '[0:-3:2]'
[1]
```

### BuildObject `{name,age}`

The BuildObject query is very powerful and can be used to create entirely new
JSON structures. The syntax of this query is exactly the same as Python but for
a couple small differences. Below is an example BuildObject query that shows
that you can put any valid Python code between the commas `,`. 

```python
{ KEY-NAME, KEY-NAME, PYTHON-CODE : PYTHON-CODE, KEY-NAME }
```

Within the commas `,`, you can put Python Dictionary-like key-value pairs and
each key and each value can be any valid Python expression. It should be noted
that the code between the commas `,` that is not a key-value pair must be the
name of a given key or an expression that evaluates to the string value of a
given key.

### Expression `(sorted(IT))`

For Pique, the Expression query is the star of the show. It is the reason why
Pique exists in the first place. It allows you to use any valid Python
expression to transform or process a JSON structure.

Here are a few examples:

```python
$ echo '[1, 2, 3, 4, 5]' | pq '(2048)'
2048
$ echo '[1, 2, 3, 4, 5]' | pq '([2, 1, 3, 1, 5])'
[2, 1, 3, 1, 5]
$ echo '[1, 2, 3, 4, 5]' | pq '(IT[2])'
3
$ echo '[1, 2, 3, 4, 5]' | pq '(len(IT))'
5
$ echo '[1, 2, 3, 4, 5]' | pq '([i ** i for i in IT])'
[1, 4, 27, 256, 3125]
```

As you can see, you can use any valid Python expression to transform the data as
you see fit.

### Fanout `[*]` & Join `[!]`

The Fanout query allows you to perform a set of queries on each element in an
array. Typical usage of Fanout can look like this:

```bash
                                           Fanout            Join
                                             |                |
                                             V                V
$ aws lambda list-functions | pq 'Functions.[*].FunctionName.[!].(len(IT))'
```

The above query will select the `"FunctionName"` key from every function in your
AWS account and then Join these names into a list. The length of the resulting
list is returned in the final query.

If a Join query is not placed at the end of the query string, it is assumed that
every query after Fanout `[*]` should be performed on every element in the
array.

### Select `[-]`

The Select query is useful if you want to filter out values that do not evaluate
to `True`. When coupled with an Expression query this becomes very powerful:

```bash
$ aws lambda list-functions | pq 'Functions.[-].(Timeout > 3)`
```

If paired with a Join query on top of that, you can perform the rest of your
queries using the filtered set of data:

```bash
$ aws lambda list-functions | pq 'Functions.[-].(Timeout > 3).[!].(len(IT))`
```

## Dotfile Support

Pique supports the use of a dotfile in your home directory named `.pq`.

This file is a valid Python file that can contain any function or class that
you would like to be available in the environment where expressions are
evaluated. For instance, if you define a function `foo()` in your `.pq` file, it
will be available in any query you make from the CLI:

```bash
$ cat example.json | pq 'key1.key2.([foo(i) for i in IT])'
```

You can also define the variable `__settings__` that can contain the keys:

 * `theme`: str
 * `indent`: integer

An example Pique dotfile may look like this:

```python
# This will be included in the eval env as `chain`:
from itertools import chain

__settings__ = {
    'theme' : 'Python3',
    'indent' : 4
}

def foo(data, index):
    return data[index] ** 10

def something():
    return 'asdf'
```

