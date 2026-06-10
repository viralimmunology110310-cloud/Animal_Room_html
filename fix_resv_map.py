import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

old_map = """      let rawDob = String(row[5] || '').trim();
      
      let sanDob = '';
      let parts = rawDob.split(/[\\/\\-.]+/).filter(Boolean);
      if (parts.length === 3) {
         let y = parts[0].length === 2 ? '20' + parts[0] : parts[0];
         let m = parts[1].padStart(2, '0');
         let d = parts[2].padStart(2, '0');
         sanDob = y + m + d;
      } else {
         sanDob = rawDob.replace(/\\D/g, '');
         if (sanDob.length === 6) sanDob = '20' + sanDob;
      }
      
      if (currentStrain && sex && head && sanDob && resv) {
         const key = currentStrain.toUpperCase() + '_' + sex + '_' + head + '_' + sanDob;
         map[key] = resv;
      }"""

new_map = """      let rawDob = row[5];
      let sanDob = '';
      if (rawDob instanceof Date) {
         let y = rawDob.getFullYear();
         let m = String(rawDob.getMonth() + 1).padStart(2, '0');
         let d = String(rawDob.getDate()).padStart(2, '0');
         sanDob = y + m + d;
      } else {
         rawDob = String(rawDob || '').trim();
         let parts = rawDob.split(/[\\/\\-.]+/).filter(Boolean);
         if (parts.length === 3) {
            let y = parts[0].length === 2 ? '20' + parts[0] : parts[0];
            let m = parts[1].padStart(2, '0');
            let d = parts[2].padStart(2, '0');
            sanDob = y + m + d;
         } else {
            sanDob = rawDob.replace(/\\D/g, '');
            if (sanDob.length === 6) sanDob = '20' + sanDob;
         }
      }
      
      if (currentStrain && sex && head && sanDob && resv) {
         const key = currentStrain.toUpperCase() + '_' + sex + '_' + head + '_' + sanDob;
         if (map[key]) {
             map[key] += ', ' + resv;
         } else {
             map[key] = resv;
         }
      }"""

content = content.replace(old_map, new_map)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)

