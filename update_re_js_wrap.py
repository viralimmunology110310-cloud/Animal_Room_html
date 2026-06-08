import re

# --- Update index.html ---
with open('index.html', 'r') as f:
    html = f.read()

html = html.replace("const APP_VERSION = 'v2.7.9';", "const APP_VERSION = 'v2.7.10';")
html = html.replace(">v2.7.9</span></h1>", ">v2.7.10</span></h1>")

with open('index.html', 'w') as f:
    f.write(html)

# --- Update apps_script/Re.js ---
with open('apps_script/Re.js', 'r') as f:
    re_js = f.read()

# 1. D.O.W to D.O.M
re_js = re_js.replace("'D.O.W'", "'D.O.M'")

# 2. Add setWrap(true) and setVerticalAlignment('middle') for Strain column
re_js = re_js.replace(
    ".setBackground(b.color);",
    ".setBackground(b.color).setWrap(true).setVerticalAlignment('middle');"
)

# And remove .setVerticalAlignment('middle') from the merge() line since we just added it above
re_js = re_js.replace(
    ".merge().setVerticalAlignment('middle');",
    ".merge();"
)

with open('apps_script/Re.js', 'w') as f:
    f.write(re_js)

print("Updates applied")
