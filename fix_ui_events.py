import re

with open('index.html', 'r') as f:
    content = f.read()

# The JS block to add
script_additions = """
    // ─── Event Listeners for UI enhancements ───
    document.addEventListener('DOMContentLoaded', () => {
        // F1 Guide
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F1' || (e.metaKey && e.key === '/')) {
                e.preventDefault();
                startTour();
            }
        });
        
        // M/F Arrow Toggle
        const bGender = document.getElementById('b-gender');
        if(bGender) {
            bGender.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.value = this.value === 'male' ? 'female' : 'male';
                }
            });
        }
        
        // Smart Date Input Parsing
        const dateInputs = document.querySelectorAll('input[type="date"], input.date-smart');
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
        });
        
        // Chip Toggles & Live update
        document.querySelectorAll('.chip-toggle input[type="checkbox"], .chip-toggle input[type="radio"]').forEach(input => {
            input.addEventListener('change', function() {
                const label = this.parentElement;
                if(this.type === 'radio') {
                    const name = this.name;
                    document.querySelectorAll(`input[name="${name}"]`).forEach(r => {
                        r.parentElement.classList.remove('active', 'active-red', 'active-blue');
                    });
                    if(this.checked) label.classList.add('active');
                } else {
                    if(this.checked) {
                        if(this.id === 'b-gdone') {
                            label.classList.add('active-red');
                            document.getElementById('b-gpre').checked = false;
                            document.getElementById('b-gpre').parentElement.classList.remove('active-blue');
                            document.getElementById('gdone-sub').style.display = 'flex';
                        } else if(this.id === 'b-gpre') {
                            label.classList.add('active-blue');
                            document.getElementById('b-gdone').checked = false;
                            document.getElementById('b-gdone').parentElement.classList.remove('active-red');
                            document.getElementById('gdone-sub').style.display = 'none';
                        } else if(this.id === 'm-pregnant') {
                            label.classList.add('active-pregnant');
                        }
                    } else {
                        label.classList.remove('active', 'active-red', 'active-blue', 'active-pregnant');
                        if(this.id === 'b-gdone') document.getElementById('gdone-sub').style.display = 'none';
                    }
                }
                
                // Live update Notes
                let noteVal = document.getElementById('m-notes').value;
                if (document.getElementById('breeding-fields').style.display !== 'none') {
                    const isGdone = document.getElementById('b-gdone').checked;
                    const isGpre = document.getElementById('b-gpre').checked;
                    const gtypeNode = document.querySelector('input[name="gtype"]:checked');
                    let gStr = '';
                    if (isGdone) gStr = gtypeNode ? `G완(${gtypeNode.value})` : 'G완';
                    else if (isGpre) gStr = 'G전';
                    
                    noteVal = noteVal.replace(/G완(?:\\([^)]+\\))?/g, '').replace(/G전/g, '').trim();
                    if (gStr) noteVal = (gStr + ' ' + noteVal).trim();
                } else if (document.getElementById('mating-fields').style.display !== 'none') {
                    const isPreg = document.getElementById('m-pregnant').checked;
                    noteVal = noteVal.replace(/\\(임신중\\)/g, '').trim();
                    if (isPreg) noteVal = ('(임신중) ' + noteVal).trim();
                }
                document.getElementById('m-notes').value = noteVal;
            });
        });
    });
"""

# Insert before function setToday
target = "    function setToday(id)"
if "Event Listeners for UI enhancements" not in content:
    content = content.replace(target, script_additions + "\n" + target)

# Remove the duplicated F1 listener if it was previously added (from my previous script)
dup_target = """        // F1 Guide
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F1') {
                e.preventDefault();
                startTour();
            }
        });"""
if "document.addEventListener('DOMContentLoaded', () => {" + dup_target in content:
    content = content.replace("document.addEventListener('DOMContentLoaded', () => {" + dup_target, "")

with open('index.html', 'w') as f:
    f.write(content)
