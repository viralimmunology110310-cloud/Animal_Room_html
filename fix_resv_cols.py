import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

old_range = "const data = resSheet.getRange('A2:H' + Math.max(2, resSheet.getLastRow())).getValues();"
new_range = "const data = resSheet.getRange('A2:K' + Math.max(2, resSheet.getLastRow())).getValues();"
content = content.replace(old_range, new_range)

old_logic = """      let otherVal = String(row[6] || '').trim();
      let resvVal = String(row[7] || '').trim();
      let resv = [otherVal, resvVal].filter(Boolean).join(', ');"""
new_logic = """      let vals = [];
      for (let c = 6; c <= 10; c++) {
        let v = String(row[c] || '').trim();
        if (v) vals.push(v);
      }
      let resv = vals.join(', ');"""
content = content.replace(old_logic, new_logic)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
