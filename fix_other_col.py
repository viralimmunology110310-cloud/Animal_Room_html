import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

old_logic = """    let currentStrain = '';
    data.forEach(row => {
      let rawStrain = String(row[0] || '').trim();
      let cageNo = String(row[1] || '').trim();
      let resv = String(row[7] || '').trim();
      
      if (rawStrain) {"""

new_logic = """    let currentStrain = '';
    data.forEach(row => {
      let rawStrain = String(row[0] || '').trim();
      let cageNo = String(row[1] || '').trim();
      
      let otherVal = String(row[6] || '').trim();
      let resvVal = String(row[7] || '').trim();
      let resv = [otherVal, resvVal].filter(Boolean).join(', ');
      
      if (rawStrain) {"""

content = content.replace(old_logic, new_logic)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
