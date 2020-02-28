# To get JSON, run this command:
# aws pinpoint phone-number-validate --region us-east-1 --number-validate-request PhoneNumber=525536747273 | python3 poc.py NumberValidateResponse
# cat input.json | python3 poc.py "Things.[*].inventory.[1]"
# aws logs describe-log-groups | python3 poc.py "logGroups.[*].logGroupName.(= '/pbz/test-log-group')"
# Using [*] always creates an array. Can I use {} to build custom objects?


import sys, json

def parse_commands(string):
    cmds = []
    for cmd in string.split('.'):
        # Index
        if cmd.startswith('['):
            cmd = cmd[1:-1]
            if cmd[0] != '*':
                cmd = int(cmd)

        # Logic expression
        elif cmd.startswith('('):
            cmd = cmd[1:-1]
        
        cmds.append(cmd)
    return cmds

def drilldown(data, commands):
    for i in range(len(commands)):
        cmd = commands[i]
        if cmd == '*':
            data = [drilldown(element, commands[i + 1:]) for element in data]
            break

        # Logic Expression
        elif cmd.startswith('='):
            op, comparison_key, arg = cmd.split()

            # Parse it into it's data type
            arg = eval(arg)

            # sys.stdin = open('/dev/tty')
            # import pdb; pdb.set_trace()

            if data[comparison_key] != arg:
                return None
            
            #data = [drilldown(element, commands[i + 1:]) for element in data]
        else:
            data = data[cmd]
    
    if isinstance(data, list):
        data = [i for i in data if i]
    return data


data = json.loads(sys.stdin.read())
if len(sys.argv) > 1:
    result = drilldown(data, parse_commands(sys.argv[1]))
else:
    result = data

print(json.dumps(result, indent=4))
