import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

# 1. Start from column 7 (H) instead of 6 (G)
old_loop = "for (let c = 6; c <= 10; c++) {"
new_loop = "for (let c = 7; c <= 10; c++) {"
content = content.replace(old_loop, new_loop)

# 2. Remove '[예약: ' and ']'
old_note = "if (resv) note = (note ? note + ', ' : '') + '[예약: ' + resv + ']';"
new_note = "if (resv) note = (note ? note + ', ' : '') + resv;"
content = content.replace(old_note, new_note)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
