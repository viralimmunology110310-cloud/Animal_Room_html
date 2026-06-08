with open('apps_script/Re.js', 'r') as f:
    code = f.read()

import re

old_func = """function buildMatingNoteRichText(noteStr, mondayStr) {
  if (!noteStr) return SpreadsheetApp.newRichTextValue().setText('').build();
  let builder = SpreadsheetApp.newRichTextValue().setText(noteStr);
  
  const regex = /Baby \d+마리\((\d{1,2})\/(\d{1,2})\)/g;
  let match;
  while ((match = regex.exec(noteStr)) !== null) {
    const mm = match[1];
    const dd = match[2];
    const dateObj = new Date(new Date().getFullYear(), parseInt(mm)-1, parseInt(dd));
    const dateStr = `${dateObj.getFullYear()}-${String(dateObj.getMonth()+1).padStart(2,'0')}-${String(dateObj.getDate()).padStart(2,'0')}`;
    const color = (dateStr >= mondayStr) ? '#FF0000' : '#0000FF';
    
    let style = SpreadsheetApp.newTextStyle()
      .setForegroundColor(color)
      .setBold(true)
      .build();
    builder.setTextStyle(match.index, match.index + match[0].length, style);
  }
  return builder.build();
}"""

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
    const color = (dateStr >= mondayStr) ? '#FF0000' : '#0000FF';
    
    let style = SpreadsheetApp.newTextStyle()
      .setForegroundColor(color)
      .setBold(true)
      .build();
    builder.setTextStyle(match.index, match.index + match[0].length, style);
  }
  return builder.build();
}"""

if old_func in code:
    code = code.replace(old_func, new_func)
else:
    print("WARNING: old_func not found in Re.js")

with open('apps_script/Re.js', 'w') as f:
    f.write(code)

print("Re.js updated")
