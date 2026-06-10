import re

with open('index.html', 'r') as f:
    content = f.read()

# 1. Floating guide button
guide_old = """<div class="help-fab-wrapper" ontouchstart=""><button class="help-fab" onclick="startTour()" title="사용법 가이드">💡</button></div>"""
guide_new = """<div class="help-fab-wrapper" ontouchstart="" style="display:none;"><button class="help-fab" onclick="startTour()" title="사용법 가이드">💡</button></div>"""
content = content.replace(guide_old, guide_new)

# Add F1 listener properly inside DOMContentLoaded if not exists
# We already have an F1 listener from last commit? Let's check if it exists.
# If not, we will add it.
if "e.key === 'F1'" not in content:
    f1_listener = """
        // F1 Guide
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F1') {
                e.preventDefault();
                startTour();
            }
        });"""
    content = content.replace("document.addEventListener('DOMContentLoaded', () => {", "document.addEventListener('DOMContentLoaded', () => {" + f1_listener)

# 2. Update CSS for gdone-sub hierarchy
css_old = """.chip-sub-row {
            display: flex; gap: 6px; align-items: center;
        }"""
css_new = """.chip-sub-row {
            display: flex; gap: 6px; align-items: center;
            background: rgba(255,255,255,0.03);
            border-left: 2px solid #ff453a;
            padding: 4px 8px;
            border-radius: 4px;
            margin-left: 4px;
        }"""
if ".chip-sub-row {" in content:
    content = re.sub(r'\.chip-sub-row\s*\{[^}]+\}', css_new, content)
else:
    # insert it
    content = content.replace("</style>", css_new + "\n    </style>")

# 3. Dynamic Notes update
# In the chip change listener:
chip_listener_old = """        document.querySelectorAll('.chip-toggle input[type="checkbox"], .chip-toggle input[type="radio"]').forEach(input => {
            input.addEventListener('change', function() {
                const label = this.parentElement;
                if(this.type === 'radio') {
                    // remove active from siblings
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
            });
        });"""

chip_listener_new = """        document.querySelectorAll('.chip-toggle input[type="checkbox"], .chip-toggle input[type="radio"]').forEach(input => {
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
        });"""
content = content.replace(chip_listener_old, chip_listener_new)

# Add (임신중) to saveCage notes processing for mating as well
# Wait, saveCage already processed info.pregnant. We just need to make sure the user's manual (임신중) is kept or updated.
# In saveCage:
save_cage_preg_old = """        if (info.type === 'mating') {
            const isPregnant = document.getElementById('m-pregnant').checked;
            info.pregnant = isPregnant;
        }"""
save_cage_preg_new = """        if (info.type === 'mating') {
            const isPregnant = document.getElementById('m-pregnant').checked;
            info.pregnant = isPregnant;
            info.notes = info.notes.replace(/\\(임신중\\)/g, '').trim();
            if (isPregnant) {
                info.notes = ('(임신중) ' + info.notes).trim();
            }
        }"""
content = content.replace(save_cage_preg_old, save_cage_preg_new)

with open('index.html', 'w') as f:
    f.write(content)

