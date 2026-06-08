import re

# --- Update index.html ---
with open('index.html', 'r') as f:
    html = f.read()

# Replace buildMatingNoteHtml
old_mating_html = """    function buildMatingNoteHtml(noteStr) {
        if (!noteStr) return '';
        const mondayStr = getMondayStr(new Date());
        let res = noteStr;
        const regex = /Baby\\s*\\d+\\s*마리\\s*\\(\\s*(\\d{1,2})\\s*\\/\\s*(\\d{1,2})\\s*\\)/g;
        let match;
        // Use replace correctly
        return res.replace(regex, (match, mm, dd) => {
            const dateObj = new Date(new Date().getFullYear(), parseInt(mm)-1, parseInt(dd));
            const dateStr = `${dateObj.getFullYear()}-${String(dateObj.getMonth()+1).padStart(2,'0')}-${String(dateObj.getDate()).padStart(2,'0')}`;
            const color = (dateStr >= mondayStr) ? '#FF0000' : '#0000FF';
            return `<span style="color:${color}; font-weight:bold;">${match}</span>`;
        });
    }"""

new_mating_html = """    function buildMatingNoteHtml(noteStr) {
        if (!noteStr) return '';
        let res = noteStr;
        const regex = /Baby\\s*\\d+\\s*마리\\s*\\(\\s*(\\d{1,2})\\s*\\/\\s*(\\d{1,2})\\s*\\)/g;
        
        const now = new Date();
        const thresholdDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
        
        return res.replace(regex, (match, mm, dd) => {
            let yyyy = now.getFullYear();
            let matchDate = new Date(yyyy, parseInt(mm)-1, parseInt(dd));
            if (matchDate > now) {
                matchDate.setFullYear(yyyy - 1);
            }
            const color = (matchDate >= thresholdDate) ? '#FF0000' : '#0000FF';
            return `<span style="color:${color}; font-weight:bold;">${match}</span>`;
        });
    }"""

if old_mating_html in html:
    html = html.replace(old_mating_html, new_mating_html)
else:
    print("Warning: old_mating_html not found in index.html")

html = html.replace("const APP_VERSION = 'v2.7.11';", "const APP_VERSION = 'v2.7.12';")
html = html.replace(">v2.7.11</span></h1>", ">v2.7.12</span></h1>")

with open('index.html', 'w') as f:
    f.write(html)


# --- Update apps_script/Re.js ---
with open('apps_script/Re.js', 'r') as f:
    re_js = f.read()

old_re_js_func = """function buildMatingNoteRichText(noteStr, mondayStr) {
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

new_re_js_func = """function buildMatingNoteRichText(noteStr) {
  if (!noteStr) return SpreadsheetApp.newRichTextValue().setText('').build();
  let builder = SpreadsheetApp.newRichTextValue().setText(noteStr);
  let blackStyle = SpreadsheetApp.newTextStyle().setForegroundColor('#000000').build();
  builder.setTextStyle(0, noteStr.length, blackStyle);
  
  const now = new Date();
  const thresholdDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
  
  const regex = /Baby\\s*\\d+\\s*마리\\s*\\(\\s*(\\d{1,2})\\s*\\/\\s*(\\d{1,2})\\s*\\)/g;
  let match;
  while ((match = regex.exec(noteStr)) !== null) {
    const mm = match[1];
    const dd = match[2];
    let yyyy = now.getFullYear();
    let matchDate = new Date(yyyy, parseInt(mm)-1, parseInt(dd));
    if (matchDate > now) {
      matchDate.setFullYear(yyyy - 1);
    }
    
    let color = (matchDate >= thresholdDate) ? '#FF0000' : '#0000FF';
    let textStyle = SpreadsheetApp.newTextStyle().setForegroundColor(color).build();
    builder.setTextStyle(match.index, match.index + match[0].length, textStyle);
  }
  return builder.build();
}"""

if old_re_js_func in re_js:
    re_js = re_js.replace(old_re_js_func, new_re_js_func)
else:
    print("Warning: old_re_js_func not found in Re.js")

# We also need to change how it's called in Re.js:
# let notesRichTexts = output.map(row => [buildMatingNoteRichText(row[8], mondayStr)]);
# to
# let notesRichTexts = output.map(row => [buildMatingNoteRichText(row[8])]);
re_js = re_js.replace("buildMatingNoteRichText(row[8], mondayStr)", "buildMatingNoteRichText(row[8])")

with open('apps_script/Re.js', 'w') as f:
    f.write(re_js)

print("7 days logic updated")
