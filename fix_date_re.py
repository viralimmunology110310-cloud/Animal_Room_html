import re

# 1. Update index.html for Date formatting and onfocus select
with open('index.html', 'r') as f:
    idx_content = f.read()

# I need to update the blur logic and add focus logic
date_js_old = """        const dateInputs = document.querySelectorAll('input[type="date"], input.date-smart');
        dateInputs.forEach(input => {
            if(input.type === 'date') {
                input.type = 'text'; // change to text for custom parsing
                input.classList.add('date-smart');
                input.placeholder = 'YYYY. MM. DD.';
            }
            input.addEventListener('blur', function() {
                let val = this.value.trim().replace(/\\D/g, '');
                if(val.length === 8) {
                    this.value = val.substring(0,4) + '-' + val.substring(4,6) + '-' + val.substring(6,8);
                } else if(val.length === 7) {
                    this.value = val.substring(0,4) + '-0' + val.substring(4,5) + '-' + val.substring(5,7);
                } else if(val.length === 4) {
                    const yr = new Date().getFullYear();
                    this.value = yr + '-' + val.substring(0,2) + '-' + val.substring(2,4);
                } else if(val.length === 3) {
                    const yr = new Date().getFullYear();
                    this.value = yr + '-0' + val.substring(0,1) + '-' + val.substring(1,3);
                }
            });
        });"""

date_js_new = """        const dateInputs = document.querySelectorAll('input[type="date"], input.date-smart');
        dateInputs.forEach(input => {
            if(input.type === 'date') {
                input.type = 'text'; // change to text for custom parsing
                input.classList.add('date-smart');
                input.placeholder = 'YYYY.M.D';
            }
            input.addEventListener('focus', function() {
                this.select();
            });
            input.addEventListener('blur', function() {
                let txt = this.value.trim();
                if (!txt) return;
                
                // Allow formats like 6/9, 2026/6/9
                let parts = txt.split(/[\\/\\-.]+/);
                let yr = new Date().getFullYear();
                let mo = '', da = '';
                
                if (parts.length === 2 && parts[0] && parts[1]) {
                    mo = parts[0]; da = parts[1];
                } else if (parts.length === 3 && parts[0] && parts[1] && parts[2]) {
                    yr = parts[0].length === 2 ? '20' + parts[0] : parts[0];
                    mo = parts[1]; da = parts[2];
                } else {
                    let val = txt.replace(/\\D/g, '');
                    if(val.length === 8) {
                        yr = val.substring(0,4); mo = val.substring(4,6); da = val.substring(6,8);
                    } else if(val.length === 6) {
                        yr = '20' + val.substring(0,2); mo = val.substring(2,4); da = val.substring(4,6);
                    } else if(val.length === 4) {
                        mo = val.substring(0,2); da = val.substring(2,4);
                    } else if(val.length === 3) {
                        mo = val.substring(0,1); da = val.substring(1,3);
                    } else if(val.length === 2) { // just day?
                        mo = new Date().getMonth()+1; da = val;
                    }
                }
                
                if (mo && da) {
                    this.value = yr + '.' + parseInt(mo) + '.' + parseInt(da);
                }
            });
        });"""

idx_content = idx_content.replace(date_js_old, date_js_new)

# Wait! The original index.html has native formatting "YYYY-MM-DD" when saveCage() pushes to Firebase.
# The `date` type inputs normally produced YYYY-MM-DD. If it now produces "2026.6.9", 
# any code depending on `YYYY-MM-DD` (like `Re.js` parsing or sorting) might break.
# Let's check saveCage in index.html, it just reads `document.getElementById('b-dob').value`.
# Firebase will just store "2026.6.9".
# In Re.js, `formatDateDots(c.bDob)` does:
#   return dStr.replace(/-/g, '.');
# So if it's already "2026.6.9", it will remain "2026.6.9", which is EXACTLY what the user wants!
# But wait, `c.bDob` and `c.mDob` are used in Re.js `getReservationMap()`!
# `let sanDob = rawDob.replace(/\D/g, ''); if (sanDob.length === 6) sanDob = '20' + sanDob;`
# Wait, `2026.6.9` -> `202669` which is 6 chars. '20' + '202669' -> '20202669' !! BUG!
# If sanDob is `202669`, it is NOT `20260609`. We need to properly pad months and days in the `sanDob` inside Re.js!

with open('index.html', 'w') as f:
    f.write(idx_content)


# 2. Update Re.js
with open('apps_script/Re.js', 'r') as f:
    re_content = f.read()

# Fix G완(분류전) color
color_old = """    if (c.notes) {
      if (c.notes.includes('G완')) color = '#FF0000';
      else if (c.notes.includes('G전')) color = '#0000FF';
    }"""
color_new = """    if (c.notes) {
      if (c.notes.includes('G완(분류전)')) color = '#0000FF';
      else if (c.notes.includes('G완')) color = '#FF0000';
      else if (c.notes.includes('G전')) color = '#0000FF';
    }"""
re_content = re_content.replace(color_old, color_new)

# Fix sanDob padding in Re.js reservation mapping
# Instead of naive replace(/\D/g, ''), we should parse it cleanly.
# A robust parse:
# const parseDobTo8Digit = d => {
#    if (!d) return '';
#    let parts = String(d).split(/[\\/\\-.]+/).filter(Boolean);
#    if (parts.length === 3) {
#       let y = parts[0].length === 2 ? '20'+parts[0] : parts[0];
#       let m = parts[1].padStart(2, '0');
#       let d = parts[2].padStart(2, '0');
#       return y + m + d;
#    }
#    let num = String(d).replace(/\\D/g, '');
#    if (num.length === 6) return '20' + num;
#    return num;
# }
res_map_old_js = """      let sanDob = rawDob.replace(/\\D/g, ''); // 2026. 06. 09. -> 20260609
      if (sanDob.length === 6) { sanDob = '20' + sanDob; }"""
res_map_new_js = """      let sanDob = '';
      let parts = rawDob.split(/[\\/\\-.]+/).filter(Boolean);
      if (parts.length === 3) {
         let y = parts[0].length === 2 ? '20' + parts[0] : parts[0];
         let m = parts[1].padStart(2, '0');
         let d = parts[2].padStart(2, '0');
         sanDob = y + m + d;
      } else {
         sanDob = rawDob.replace(/\\D/g, '');
         if (sanDob.length === 6) sanDob = '20' + sanDob;
      }"""
re_content = re_content.replace(res_map_old_js, res_map_new_js)

mating_res_old_js = """    const sanDobM = c.mDob ? String(c.mDob).replace(/\\D/g, '') : '';
    const sanDobF = c.fDob ? String(c.fDob).replace(/\\D/g, '') : '';"""
mating_res_new_js = """    const parseDob = (raw) => {
      if (!raw) return '';
      let p = String(raw).split(/[\\/\\-.]+/).filter(Boolean);
      if (p.length === 3) return (p[0].length===2?'20'+p[0]:p[0]) + p[1].padStart(2,'0') + p[2].padStart(2,'0');
      let n = String(raw).replace(/\\D/g, ''); return n.length===6 ? '20'+n : n;
    };
    const sanDobM = parseDob(c.mDob);
    const sanDobF = parseDob(c.fDob);"""
re_content = re_content.replace(mating_res_old_js, mating_res_new_js)

breeding_res_old_js = """    const sanDob = c.bDob ? String(c.bDob).replace(/\\D/g, '') : '';"""
breeding_res_new_js = """    const parseDob = (raw) => {
      if (!raw) return '';
      let p = String(raw).split(/[\\/\\-.]+/).filter(Boolean);
      if (p.length === 3) return (p[0].length===2?'20'+p[0]:p[0]) + p[1].padStart(2,'0') + p[2].padStart(2,'0');
      let n = String(raw).replace(/\\D/g, ''); return n.length===6 ? '20'+n : n;
    };
    const sanDob = parseDob(c.bDob);"""
re_content = re_content.replace(breeding_res_old_js, breeding_res_new_js)


with open('apps_script/Re.js', 'w') as f:
    f.write(re_content)

