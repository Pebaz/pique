import nimpy, tables

let py = pyBuiltinsModule()

echo py.eval(
    """ [i for i in key + other] """,
    to_table({"key": "value", "other": "things"})
)
