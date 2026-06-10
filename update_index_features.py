import re

with open('index.html', 'r') as f:
    content = f.read()

# 1. Update checkAndSaveSnapshot and call it
snapshot_func_old = """    function checkAndSaveSnapshot(data) {
        const todayStr = getMondayStr(new Date()).replace(/-\\d{2}$/, '-' + String(new Date().getDate()).padStart(2,'0')); // YYYY-MM-DD
        fbDb.ref('snapshots/lastDate').once('value').then(snap => {
            if (snap.val() !== todayStr) {
                let updates = {};
                updates['snapshots/lastDate'] = todayStr;
                updates['snapshots/' + todayStr] = data;
                fbDb.update(updates).then(() => console.log('Daily snapshot saved:', todayStr));
            }
        });
    }"""
snapshot_func_new = """    function checkAndSaveSnapshot(data) {
        const d = new Date();
        const todayStr = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
        fbDb.ref('snapshots/lastDate').once('value').then(snap => {
            if (snap.val() !== todayStr) {
                let updates = {};
                updates['snapshots/lastDate'] = todayStr;
                updates['snapshots/' + todayStr] = data;
                fbDb.update(updates).then(() => {
                    console.log('Daily snapshot saved:', todayStr);
                    // 2주 지난 스냅샷 자동 삭제
                    fbDb.ref('snapshots').once('value').then(allSnaps => {
                        const cutoff = new Date();
                        cutoff.setDate(cutoff.getDate() - 14);
                        const cutoffStr = cutoff.getFullYear() + '-' + String(cutoff.getMonth() + 1).padStart(2, '0') + '-' + String(cutoff.getDate()).padStart(2, '0');
                        allSnaps.forEach(child => {
                            if (child.key !== 'lastDate' && child.key < cutoffStr) {
                                fbDb.ref('snapshots/' + child.key).remove();
                                console.log('Old snapshot deleted:', child.key);
                            }
                        });
                    });
                });
            }
        });
    }"""
content = content.replace(snapshot_func_old, snapshot_func_new)

# Call checkAndSaveSnapshot in Firebase listener
call_snapshot = "isDataLoaded = true;\n        checkAndSaveSnapshot(data);"
content = content.replace("isDataLoaded = true;", call_snapshot)

# 2. Add Event Listener for Arrow keys on gender select
# And Date parsing logic
script_additions = """
    // ─── Event Listeners for UI enhancements ───
    document.addEventListener('DOMContentLoaded', () => {
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
                input.placeholder = 'YYYYMMDD';
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
        
        // Chip Toggles
        document.querySelectorAll('.chip-toggle input[type="checkbox"], .chip-toggle input[type="radio"]').forEach(input => {
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
        });
    });
"""
content = content.replace("function setToday(id)", script_additions + "\n    function setToday(id)")

# 3 & 4 HTML additions for Breeding G완/G전 and Mating Pregnant
breeding_html_old = """        <!-- Breeding fields -->
        <div id="breeding-fields">"""
breeding_html_new = """        <!-- Breeding fields -->
        <div id="breeding-fields">
            <div class="chip-row">
                <label class="chip-toggle"><input type="checkbox" id="b-gdone"> <span>G완</span></label>
                <div id="gdone-sub" class="chip-sub-row" style="display:none">
                    <label class="chip-toggle sub"><input type="radio" name="gtype" value="homo"> homo</label>
                    <label class="chip-toggle sub"><input type="radio" name="gtype" value="het"> het</label>
                    <label class="chip-toggle sub"><input type="radio" name="gtype" value="tg"> tg</label>
                    <label class="chip-toggle sub"><input type="radio" name="gtype" value="분류전"> 분류전</label>
                </div>
                <label class="chip-toggle"><input type="checkbox" id="b-gpre"> <span>G전</span></label>
            </div>"""
content = content.replace(breeding_html_old, breeding_html_new)

mating_html_old = """        <!-- Mating fields -->
        <div id="mating-fields">"""
mating_html_new = """        <!-- Mating fields -->
        <div id="mating-fields">
            <div class="chip-row">
                <label class="chip-toggle pregnant-toggle"><input type="checkbox" id="m-pregnant"> <span>🤰 임신중</span></label>
            </div>"""
content = content.replace(mating_html_old, mating_html_new)

# 5. Baby note formatting + notes saving logic
save_cage_logic_old = """            notes: document.getElementById('m-notes').value,
            dom: document.getElementById('m-dom').value,"""
save_cage_logic_new = """            notes: document.getElementById('m-notes').value,
            dom: document.getElementById('m-dom').value,"""
# Actually, let's put the parsing inside saveCage right before startTransaction
parse_notes_old = "startTransaction();"
parse_notes_new = """
        // Auto-format Baby notes
        if(info.notes) {
            info.notes = info.notes.replace(/baby\\s*(\\d+)\\s*(?:마리)?\\s*\\(\\s*(\\d{1,2})\\s*\\/\\s*(\\d{1,2})\\s*\\)/gi, 'Baby $1마리($2/$3)');
        }
        
        // Append G완/G전 and Pregnant if applicable
        if (info.type === 'breeding' || info.type === 'experiment') {
            const isGdone = document.getElementById('b-gdone').checked;
            const isGpre = document.getElementById('b-gpre').checked;
            const gtypeNode = document.querySelector('input[name="gtype"]:checked');
            let gStr = '';
            if (isGdone) {
                gStr = gtypeNode ? `G완(${gtypeNode.value})` : 'G완';
            } else if (isGpre) {
                gStr = 'G전';
            }
            if (gStr) {
                // remove existing G완/G전
                info.notes = info.notes.replace(/G완(?:\\([^)]+\\))?/g, '').replace(/G전/g, '').trim();
                info.notes = (gStr + ' ' + info.notes).trim();
            }
        }
        
        if (info.type === 'mating') {
            const isPregnant = document.getElementById('m-pregnant').checked;
            info.pregnant = isPregnant;
        }

        startTransaction();"""
content = content.replace(parse_notes_old, parse_notes_new)

# 6. openModal logic to check checkboxes
open_modal_old = """            document.getElementById('m-notes').value = c.notes || '';"""
open_modal_new = """            document.getElementById('m-notes').value = c.notes || '';
            
            // Reset chips
            document.querySelectorAll('.chip-toggle input').forEach(el => { el.checked = false; el.parentElement.classList.remove('active', 'active-red', 'active-blue', 'active-pregnant'); });
            document.getElementById('gdone-sub').style.display = 'none';
            
            // Set Pregnant
            if (c.pregnant) {
                document.getElementById('m-pregnant').checked = true;
                document.getElementById('m-pregnant').parentElement.classList.add('active-pregnant');
            }
            
            // Parse G완/G전 from notes
            if (c.notes) {
                const gdoneMatch = c.notes.match(/G완(?:\\(([^)]+)\\))?/);
                if (gdoneMatch) {
                    const chk = document.getElementById('b-gdone');
                    chk.checked = true; chk.parentElement.classList.add('active-red');
                    document.getElementById('gdone-sub').style.display = 'flex';
                    if (gdoneMatch[1]) {
                        const r = document.querySelector(`input[name="gtype"][value="${gdoneMatch[1]}"]`);
                        if (r) { r.checked = true; r.parentElement.classList.add('active'); }
                    }
                } else if (c.notes.includes('G전')) {
                    const chk = document.getElementById('b-gpre');
                    chk.checked = true; chk.parentElement.classList.add('active-blue');
                }
            }
"""
content = content.replace(open_modal_old, open_modal_new)

# openModal else logic (new cage)
open_modal_else_old = """            document.getElementById('m-notes').value = '';"""
open_modal_else_new = """            document.getElementById('m-notes').value = '';
            document.querySelectorAll('.chip-toggle input').forEach(el => { el.checked = false; el.parentElement.classList.remove('active', 'active-red', 'active-blue', 'active-pregnant'); });
            document.getElementById('gdone-sub').style.display = 'none';"""
content = content.replace(open_modal_else_old, open_modal_else_new)

# visual indicator for pregnant on board
render_pane_old = """            const cageHtml = `
                <div class="cage" id="${c.id}" data-type="${c.type}" style="left:${x}px; top:${y}px; ${colorStyle}">
                    <div style="font-size:15px; letter-spacing:0.5px;">${c.code || ''}</div>
                    <div style="font-size:15px; margin-top:2px;">${c.subId || ''}</div>
                    ${iconHtml}
                </div>`;"""
render_pane_new = """            const pregIndicator = c.pregnant ? '<div class="pregnant-indicator">🤰</div>' : '';
            const cageHtml = `
                <div class="cage" id="${c.id}" data-type="${c.type}" style="left:${x}px; top:${y}px; ${colorStyle}">
                    <div style="font-size:15px; letter-spacing:0.5px;">${c.code || ''}</div>
                    <div style="font-size:15px; margin-top:2px;">${c.subId || ''}</div>
                    ${iconHtml}
                    ${pregIndicator}
                </div>`;"""
content = content.replace(render_pane_old, render_pane_new)

# Log clear logic fix
clear_logs_old = """    function clearLogsSite() {
        if(confirm('모든 수정 로그를 삭제하시겠습니까?\\n서버(구글 시트)에도 빈 로그로 즉시 덮어씌워집니다.')) {
            editLog = [];
            saveLog();
            refreshLogPanel();
            debouncedSyncToSheet();
        }
    }"""
clear_logs_new = """    function clearLogsSite() {
        if(confirm('모든 수정 로그를 삭제하시겠습니까?\\n서버(구글 시트)에도 빈 로그로 즉시 덮어씌워집니다.')) {
            editLog = [];
            saveLog();
            refreshLogPanel();
            if (fbDataRef) {
                fbDataRef.update({ logs: [] }).then(() => {
                    debouncedPushToSheet();
                });
            }
        }
    }"""
content = content.replace(clear_logs_old, clear_logs_new)

# 'G완(분류전)' -> blue color styling for notes
breeding_note_color_old = """    function getBreedingNoteColor(n) {
        if (!n) return '#8e8e93';
        if (n.includes('G완')) return '#FF0000';
        if (n.includes('G전')) return '#0000FF';
        return '#8e8e93';
    }"""
breeding_note_color_new = """    function getBreedingNoteColor(n) {
        if (!n) return '#8e8e93';
        if (n.includes('G완(분류전)')) return '#0000FF'; // Requested: 분류전 is blue
        if (n.includes('G완')) return '#FF0000';
        if (n.includes('G전')) return '#0000FF';
        return '#8e8e93';
    }"""
content = content.replace(breeding_note_color_old, breeding_note_color_new)

with open('index.html', 'w') as f:
    f.write(content)
