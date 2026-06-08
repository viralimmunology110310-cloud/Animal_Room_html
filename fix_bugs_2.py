import re

with open('index.html', 'r') as f:
    code = f.read()

# 1. Add Snapshot UI to Log Panel
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
if "🚨 데이터 긴급 복구" not in code:
    code = code.replace("    </div></div>\n", "    </div>" + restore_ui + "\n")

# 2. Update Version to v2.7.9
code = code.replace("const APP_VERSION = 'v2.7.8';", "const APP_VERSION = 'v2.7.9';")
code = code.replace(">v2.7.8</span></h1>", ">v2.7.9</span></h1>")

with open('index.html', 'w') as f:
    f.write(code)


# --- Fix Re.js ---
with open('apps_script/Re.js', 'r') as f:
    re_js = f.read()

# I want to make sure rowData[2] = c.subId in Mating, and rowData[2] = strainCNo in Breeding.
# In formatBreedingSheet, rowData[0] = bCol; rowData[1] = globalNo++; rowData[2] = c.subId; ...
breeding_replace = """    let rowData = new Array(15).fill('');
    rowData[0] = bCol;
    rowData[1] = globalNo++;
    rowData[2] = strainCNo;
    rowData[3] = strainName;
    rowData[4] = sex;"""

# Replace in Breeding Sheet
re_js = re.sub(
    r"    let rowData = new Array\(15\)\.fill\(''\);\n    rowData\[0\] = bCol;\n    rowData\[1\] = globalNo\+\+;\n    rowData\[2\] = c\.subId;\n    rowData\[3\] = strainName;\n    rowData\[4\] = sex;",
    breeding_replace,
    re_js
)

with open('apps_script/Re.js', 'w') as f:
    f.write(re_js)

print("Bugs fixed 2")
