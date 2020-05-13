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

## Usage

```bash
$ cat example.json | pq

$ echo '{ "name" : "Pebaz" }' | pq name  # "Pebaz"
```



## Tutorial

There are only 7 query types in Pique:

 * SelectKey: `keyname`
 * Index: `[123]`
 * BuildObject: `{name,age,"address":address.uppper(),phone}`
 * Expression: `(i for i in range(10))`
 * Fanout: `[*]`
 * Join: `[!]`
 * Select: `[-]`

### Fanout `[*]` & Join `[!]`

The Fanout query allows you to perform a set of queries on each element in an
array. Typical usage of Fanout can look like this:

```bash
                                           Fanout    Join
                                             |        |
                                             V        V
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

