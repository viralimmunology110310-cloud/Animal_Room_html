with open('apps_script/Re.js', 'r') as f:
    code = f.read()

import re

old_func_pattern = r"function buildMatingNoteRichText\(noteStr, mondayStr\) \{.*?\n\}"
old_match = re.search(old_func_pattern, code, flags=re.DOTALL)

new_func = """function buildMatingNoteRichText(noteStr, mondayStr) {
  if (!noteStr) return SpreadsheetApp.newRichTextValue().setText('').build();
  let builder = SpreadsheetApp.newRichTextValue().setText(noteStr);
  let blackStyle = SpreadsheetApp.newTextStyle().setForegroundColor('#000000').build();
  builder.setTextStyle(0, noteStr.length, blackStyle);
  
  const regex = /Baby\\s*\\d+\\s*마리\\s*\\(\\s*(\\d{1,2})\\s*\\/\\s*(\\d{1,2})\\s*\\)/g;
  let match;
  while ((match = regex.exec(noteStr)) !== null) {
    const mm = match[1];
    const dd = match[2];
    const dateObj = new Date(new Date().getFullYear(), parseInt(mm)-1, parseInt(dd));
    const dateStr = `${dateObj.getFullYear()}-${String(dateObj.getMonth()+1).padStart(2,'0')}-${String(dateObj.getDate()).padStart(2,'0')}`;
    let color = '#0000FF'; // Blue
    if (dateStr >= mondayStr) {
      color = '#FF0000'; // Red
    }
    let textStyle = SpreadsheetApp.newTextStyle().setForegroundColor(color).build();
    builder.setTextStyle(match.index, match.index + match[0].length, textStyle);
  }
  return builder.build();
}"""

if old_match:
    code = code.replace(old_match.group(0), new_func)

with open('apps_script/Re.js', 'w') as f:
    f.write(code)
print("Re.js updated")
