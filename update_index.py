import re

with open('index.html', 'r') as f:
    code = f.read()

# 1. Update Version and SCRIPT_URL
code = code.replace("const APP_VERSION = 'v2.7.6';", "const APP_VERSION = 'v2.7.7';")
code = code.replace(">v2.7.6</span></h1>", ">v2.7.7</span></h1>")
code = re.sub(
    r"const SCRIPT_URL = 'https://script.google.com/macros/s/.*?/exec';",
    "const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbzLkCpTPHVb6bGVE7wE564rYT2GS0eu8G7rTE0kqgi-qOCHJ2_vYKuoVdBzShfuxQ7k/exec';",
    code
)

# 2. Add Snapshot UI
snapshot_ui = """
        <button class="header-btn btn-log-view" onclick="openLogPanel()">📄 로그 / 복구</button>
"""
code = code.replace('<button class="header-btn btn-log-view" onclick="openLogPanel()">📄 로그 보기</button>', snapshot_ui)

restore_ui = """
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #444;">
            <button class="config-btn" style="background:#ff3b30; width:100%;" onclick="openSnapshotModal()">🚨 데이터 긴급 복구 (과거 시점으로 되돌리기)</button>
        </div>
    </div>
</div>

<!-- Snapshot Modal -->
<div id="snapshot-modal" class="modal-overlay">
    <div class="modal-content" style="max-width:400px;">
        <h3 style="margin-top:0; color:#ff3b30;">데이터 긴급 복구</h3>
        <p style="font-size:12px; color:#ccc;">복구 가능한 과거 시점 목록입니다. 선택 시 현재 데이터가 덮어씌워집니다.</p>
        <div id="snapshot-list" style="max-height:200px; overflow-y:auto; margin: 10px 0; background:#111; border-radius:5px; padding:10px;">
            <div style="color:#888; font-size:12px; text-align:center;">목록을 불러오는 중...</div>
        </div>
        <div class="modal-btns">
            <button class="modal-btn cancel-btn" onclick="document.getElementById('snapshot-modal').style.display='none'">닫기</button>
        </div>
    </div>
</div>
"""
code = code.replace('    </div>\n</div>\n\n<!-- Match Settings Modal -->', restore_ui + '\n\n<!-- Match Settings Modal -->')

snapshot_script = """
    function openSnapshotModal() {
        closeLogPanel();
        document.getElementById('snapshot-modal').style.display = 'flex';
        const listDiv = document.getElementById('snapshot-list');
        listDiv.innerHTML = '<div style="color:#888; font-size:12px; text-align:center;">목록을 불러오는 중...</div>';
        
        fbDb.ref('snapshots').once('value').then(snapshot => {
            const data = snapshot.val();
            if (!data) {
                listDiv.innerHTML = '<div style="color:#888; font-size:12px; text-align:center;">저장된 스냅샷이 없습니다.</div>';
                return;
            }
            const keys = Object.keys(data).filter(k => k !== 'lastDate').sort().reverse();
            if (keys.length === 0) {
                listDiv.innerHTML = '<div style="color:#888; font-size:12px; text-align:center;">저장된 스냅샷이 없습니다.</div>';
                return;
            }
            let html = '';
            keys.forEach(k => {
                html += `<div style="padding:8px; border-bottom:1px solid #333; display:flex; justify-content:space-between; align-items:center;">
                    <span>${k}</span>
                    <button class="config-btn" style="padding:4px 8px; font-size:11px;" onclick="restoreSnapshot('${k}')">복구</button>
                </div>`;
            });
            listDiv.innerHTML = html;
        }).catch(err => {
            listDiv.innerHTML = '<div style="color:#ff3b30; font-size:12px; text-align:center;">오류가 발생했습니다.</div>';
        });
    }

    function restoreSnapshot(dateKey) {
        if (!confirm(`${dateKey} 시점으로 데이터를 복구하시겠습니까?\\n현재 데이터는 유실됩니다!`)) return;
        fbDb.ref('snapshots/' + dateKey).once('value').then(snapshot => {
            const data = snapshot.val();
            if (data) {
                fbDataRef.set(data).then(() => {
                    alert('복구가 완료되었습니다. 페이지를 새로고침합니다.');
                    location.reload();
                });
            }
        });
    }

    function checkAndSaveSnapshot(data) {
        const todayStr = getMondayStr(new Date()).replace(/-\\d{2}$/, '-' + String(new Date().getDate()).padStart(2,'0')); // YYYY-MM-DD
        fbDb.ref('snapshots/lastDate').once('value').then(snap => {
            if (snap.val() !== todayStr) {
                let updates = {};
                updates['snapshots/lastDate'] = todayStr;
                updates['snapshots/' + todayStr] = data;
                fbDb.update(updates).then(() => console.log('Daily snapshot saved:', todayStr));
            }
        });
    }
"""
code = code.replace('function openLogPanel()', snapshot_script + '\n    function openLogPanel()')

# Call checkAndSaveSnapshot in saveToFirebase
code = code.replace('fbDataRef.set(dataToSave).then(() => {', 'fbDataRef.set(dataToSave).then(() => { checkAndSaveSnapshot(dataToSave); ')

# 3. Mating Baby note coloring and G완/G전 logic
note_logic = """
    function getMondayStr(d) {
        var d2 = new Date(d);
        var day = d2.getDay(), diff = d2.getDate() - day + (day == 0 ? -6:1);
        d2.setDate(diff);
        return `${d2.getFullYear()}-${String(d2.getMonth()+1).padStart(2,'0')}-${String(d2.getDate()).padStart(2,'0')}`;
    }

    function buildMatingNoteHtml(noteStr) {
        if (!noteStr) return '';
        const mondayStr = getMondayStr(new Date());
        let res = noteStr;
        const regex = /Baby \\d+마리\\((\\d{1,2})\\/(\\d{1,2})\\)/g;
        let match;
        // Use replace correctly
        return res.replace(regex, (match, mm, dd) => {
            const dateObj = new Date(new Date().getFullYear(), parseInt(mm)-1, parseInt(dd));
            const dateStr = `${dateObj.getFullYear()}-${String(dateObj.getMonth()+1).padStart(2,'0')}-${String(dateObj.getDate()).padStart(2,'0')}`;
            const color = (dateStr >= mondayStr) ? '#FF0000' : '#0000FF';
            return `<span style="color:${color}; font-weight:bold;">${match}</span>`;
        });
    }
"""
code = code.replace('function getBreedingNoteColor(n)', note_logic + '\n    function getBreedingNoteColor(n)')

# Use regex to replace c.notes safely in renderSheetPane
# Because the string might have changed formatting, let's just replace the exact line for mating
code = code.replace('<td style="color:${getMatingNoteColor(c)}; text-align:left;">${c.notes || \'\'}</td>', '<td style="color:#000000; text-align:left;">${buildMatingNoteHtml(c.notes || \'\')}</td>')

# Fix G완/G전 순서 in index.html (there isn't one directly rendered in index.html like Re.js, but let's check)
# Actually the G전/G완 text in Strain merge is generated by index.html too?
# In renderSheetPane:
if 'G전: ${b.g_pre} / G완: ${b.g_done_heads}' in code:
    code = code.replace('G전: ${b.g_pre} / G완: ${b.g_done_heads}', 'G완: ${b.g_done_heads} / G전: ${b.g_pre}')

# 4. Red hover border for Right tables and Main board triggers
css = """
        .hover-border-red td {
            border-top: 2px solid #FF3B30 !important;
            border-bottom: 2px solid #FF3B30 !important;
        }
        .hover-border-red td:first-child { border-left: 2px solid #FF3B30 !important; }
        .hover-border-red td:last-child { border-right: 2px solid #FF3B30 !important; }
"""
code = code.replace('</style>', css + '\n</style>')

# Remove old highlight-blink from hoverSidebarRow
code = code.replace("el.classList.add('highlight-blink');", "el.classList.add('hover-border-red');")
code = code.replace("el.classList.remove('highlight-blink');", "el.classList.remove('hover-border-red');")

# Add hover triggers to main board cages
code = re.sub(
    r"onclick=\"openModal\('\$\{c\.id\}'\)\" title=",
    r"onmouseenter=\"hoverSidebarRow('${c.id}')\" onmouseleave=\"unhoverSidebarRow('${c.id}')\" onclick=\"openModal('${c.id}')\" title=",
    code
)

# 5. Fix DOB format
code = re.sub(
    r"function formatDOB\(dobStr\) \{.*?\n\}",
    r"""function formatDOB(dobStr) {
    if (!dobStr) return '';
    const d = new Date(dobStr);
    if (isNaN(d.getTime())) return dobStr;
    return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`;
}""",
    code,
    flags=re.DOTALL
)

with open('index.html', 'w') as f:
    f.write(code)

print("Updated index.html")
