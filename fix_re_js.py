with open('apps_script/Re.js', 'r') as f:
    code = f.read()

import re
old_block = re.search(r"      let builder = SpreadsheetApp\.newRichTextValue\(\)\.setText\(c\.notes\);.*?sheet\.getRange\(b\.start, 7, b\.num, 1\)\.setRichTextValue\(builder\.build\(\)\);", code, flags=re.DOTALL).group(0)

new_block = """      if (c.notes) {
        let builder = SpreadsheetApp.newRichTextValue().setText(c.notes);
        let blackStyle = SpreadsheetApp.newTextStyle().setForegroundColor('#000000').build();
        builder.setTextStyle(0, c.notes.length, blackStyle);
        
        let match = c.notes.match(/Baby\\s*\\d+\\s*마리\\s*\\(\\s*([\\d/]+)\\s*\\)/);
        if (match) {
          let dateParts = match[1].split('/');
          if (dateParts.length === 2) {
            let yyyy = new Date().getFullYear();
            let mm = parseInt(dateParts[0], 10) - 1;
            let dd = parseInt(dateParts[1], 10);
            let matchDate = new Date(yyyy, mm, dd);
            let matchDateStr = `${matchDate.getFullYear()}-${String(matchDate.getMonth()+1).padStart(2,'0')}-${String(matchDate.getDate()).padStart(2,'0')}`;
            
            let color = (matchDateStr >= mondayStr) ? '#FF0000' : '#0000FF';
            let style = SpreadsheetApp.newTextStyle()
              .setForegroundColor(color)
              .setBold(true)
              .build();
              
            let startIndex = match.index;
            let endIndex = startIndex + match[0].length;
            builder.setTextStyle(startIndex, endIndex, style);
          }
        }
        sheet.getRange(b.start, 7, b.num, 1).setRichTextValue(builder.build());
      } else {
        sheet.getRange(b.start, 7, b.num, 1).setValue('');
      }"""

code = code.replace(old_block, new_block)

with open('apps_script/Re.js', 'w') as f:
    f.write(code)

print("Re.js fixed")
