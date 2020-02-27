# To get JSON, run this command:
# aws pinpoint phone-number-validate --region us-east-1 --number-validate-request PhoneNumber=525536747273 | python3 poc.py NumberValidateResponse

import sys, json

def parse_commands(string):
    cmds = []
    for cmd in string.split('.'):
        if cmd.startswith('['):
            cmd = cmd[1:-1]
            if cmd[0] != '*':
                cmd = int(cmd)
        cmds.append(cmd)
    return cmds

def drilldown(data, commands):
    for i in range(len(commands)):
        cmd = commands[i]
        if cmd == '*':
            data = [drilldown(element, commands[i + 1:]) for element in data]
            break
        else:
            data = data[cmd]
    return data


data = json.loads(sys.stdin.read())
result = drilldown(data, parse_commands(sys.argv[1]))

print(json.dumps(result, indent=4))
