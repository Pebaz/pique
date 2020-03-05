

# Use pique like a library

for name in pique.query(data, "Functions.[*].FunctionName"):
    print(name)
