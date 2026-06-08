import re

with open('index.html', 'r') as f:
    code = f.read()

# Update Firebase references
code = code.replace("fbDb.ref('snapshots')", "fbDb.ref('dev_snapshots')")
code = code.replace("fbDb.ref('snapshots/'", "fbDb.ref('dev_snapshots/'")
code = code.replace("fbDb.ref('animalRoom')", "fbDb.ref('dev_animalRoom')")

# Update SCRIPT_URL
old_script = "const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbz0VhPwDY8CGuxA4D9unK3bOxTuryx0Wpq5M2MFJRNfMvVphTqdFmS2Vz2el8PvIwKC/exec';"
new_script = "const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwBjXf8HAhsE0C_rCP_wwrmGRxDGVpiN1r-vJs7WZkn8e4-yVghDG_jZBp9OqiqzHjz/exec';"
code = code.replace(old_script, new_script)

# Update APP_VERSION
code = code.replace("const APP_VERSION = 'v2.7.17';", "const APP_VERSION = 'v3.0.0-dev';")

with open('index.html', 'w') as f:
    f.write(code)

print("Dev environment updated in index.html")
