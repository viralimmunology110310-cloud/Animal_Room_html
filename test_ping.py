import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

debug_get = """function doGet(e) {
  return ContentService.createTextOutput("PING SUCCESS");
}
"""

content = re.sub(r'function doGet\(e\) \{.*?\nfunction doPost\(e\) \{', debug_get + '\nfunction doPost(e) {', content, flags=re.DOTALL)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
