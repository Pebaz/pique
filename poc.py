# To get JSON, run this command:
# aws pinpoint phone-number-validate --region us-east-1 --number-validate-request PhoneNumber=525536747273 | python3 poc.py NumberValidateResponse

import sys, json

data = json.loads(sys.stdin.read())

command = sys.argv[1:]

result = data
for key in command:
    result = result[key]

print(json.dumps(result, indent=4))
