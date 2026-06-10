import re

with open('Re.js', 'r') as f:
    content = f.read()

new_get = """function doGet(e) {
  try {
    const map = getReservationMap();
    return ContentService.createTextOutput(JSON.stringify(map));
  } catch(e) {
    return ContentService.createTextOutput(e.toString());
  }
}
"""

content = re.sub(r'function doGet\(e\) \{.*?\nfunction doPost\(e\) \{', new_get + '\nfunction doPost(e) {', content, flags=re.DOTALL)

with open('Re.js', 'w') as f:
    f.write(content)
