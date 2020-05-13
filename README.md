# Pique

> Query JSON from the CLI using Python syntax

## What is Pique

Pique is a command line JSON query and processing tool similar to
[JQ](https://stedolan.github.io/jq/) and [JMESPath](https://jmespath.org/).

However, while these other applications are highly useful, they introduce yet
another query language to learn. With Pique, you can use any valid Python
expression in your queries, bringing the full power of Python to your CLI.


## Installation

```bash
$ pip install python-pique
```

## Usage

```bash
$ echo '{ "name" : "Pebaz" }' | pq name
-> Pebaz
```

```
         Fanout    Join
           |        |
           V        V
Functions.[*].Name.[!].(len(IT))
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


