with open('index.html', 'r') as f:
    code = f.read()

old_regex = "const regex = /Baby \d+마리\((\d{1,2})\/(\d{1,2})\)/g;"
new_regex = "const regex = /Baby\\s*\\d+\\s*마리\\s*\\(\\s*(\\d{1,2})\\s*\\/\\s*(\\d{1,2})\\s*\\)/g;"
code = code.replace(old_regex, new_regex)

with open('index.html', 'w') as f:
    f.write(code)
