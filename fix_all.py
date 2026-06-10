import re

# 1. Update index.html
with open('index.html', 'r') as f:
    idx = f.read()

idx = idx.replace("noteVal = noteVal.replace(/\\(임신중\\)/g, '').trim();", "noteVal = noteVal.replace(/\\(?임신중\\)?\\s*/g, '').trim();")
idx = idx.replace("if (isPreg) noteVal = ('(임신중) ' + noteVal).trim();", "if (isPreg) noteVal = ('임신중 ' + noteVal).trim();")

idx = idx.replace("info.notes = info.notes.replace(/\\(임신중\\)/g, '').trim();", "info.notes = info.notes.replace(/\\(?임신중\\)?\\s*/g, '').trim();")
idx = idx.replace("info.notes = ('(임신중) ' + info.notes).trim();", "info.notes = ('임신중 ' + info.notes).trim();")

old_color = """    function getBreedingNoteColor(n) {
            if (!n) return '#000000';
            if (n.includes('G완')) return '#FF0000';
            if (n.includes('G전')) return '#0000FF';
            return '#000000';
        }"""
new_color = """    function getBreedingNoteColor(n) {
            if (!n) return '#000000';
            if (n.includes('G완(분류전)')) return '#0000FF';
            if (n.includes('G완')) return '#FF0000';
            if (n.includes('G전')) return '#0000FF';
            return '#000000';
        }"""
idx = idx.replace(old_color, new_color)

with open('index.html', 'w') as f:
    f.write(idx)


# 2. Update Re.js
with open('apps_script/Re.js', 'r') as f:
    re_js = f.read()

# Replace note formatting
re_js = re_js.replace("if (resv) note = (note ? note + '\\n' : '') + '[예약: ' + resv + ']';", "if (resv) note = (note ? note + ', ' : '') + '[예약: ' + resv + ']';")

# Replace reservationMap to strip (g완) from the strain column
old_map = """      let currentStrain = '';
    data.forEach(row => {
      let rawStrain = String(row[0] || '').trim();
      let cageNo = String(row[1] || '').trim();
      let resv = String(row[7] || '').trim();
      
      if (rawStrain) {
         currentStrain = rawStrain;
      }"""
new_map = """      let currentStrain = '';
    data.forEach(row => {
      let rawStrain = String(row[0] || '').trim();
      let cageNo = String(row[1] || '').trim();
      let resv = String(row[7] || '').trim();
      
      if (rawStrain) {
         // Remove (G완), (g완) or anything in parentheses so 'C(G완)' becomes 'C'
         currentStrain = rawStrain.replace(/\\s*\\([^)]*\\)\\s*/g, '');
      }"""
re_js = re_js.replace(old_map, new_map)

with open('apps_script/Re.js', 'w') as f:
    f.write(re_js)

