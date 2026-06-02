import re

# --- Fix index.html ---
with open('index.html', 'r') as f:
    code = f.read()

# 1. Restore hover logic
hover_func = """    window.hoverSidebarRow = function(cageId) {
        const toggle = document.getElementById('toggle-highlight');
        if (toggle && !toggle.checked) return;

        const c = cages.find(x => x.id === cageId);
        if (!c) return;
        if (c.rackId !== currentRack) {
            currentRack = c.rackId;
            buildLeftSidebar();
            renderMainBoard();
        }
        const el = document.getElementById(cageId);
        if (el) el.classList.add('highlight-blink');
        
        const rowM = document.getElementById(`row-mating-${cageId}`);
        if (rowM) rowM.classList.add('hover-border-red');
        const rowB = document.getElementById(`row-breeding-${cageId}`);
        if (rowB) rowB.classList.add('hover-border-red');
    };

    window.unhoverSidebarRow = function(cageId) {
        const el = document.getElementById(cageId);
        if (el) el.classList.remove('highlight-blink');
        const rowM = document.getElementById(`row-mating-${cageId}`);
        if (rowM) rowM.classList.remove('hover-border-red');
        const rowB = document.getElementById(`row-breeding-${cageId}`);
        if (rowB) rowB.classList.remove('hover-border-red');
    };"""
code = re.sub(
    r"    window\.hoverSidebarRow = function\(cageId\).*?window\.unhoverSidebarRow = function\(cageId\) \{.*?\n    \};",
    hover_func,
    code,
    flags=re.DOTALL
)

# 2. Fix Snapshot Button
# The UI replace failed last time because the button was "📋 로그" not "📄 로그 보기"
if '<button class="header-btn" onclick="openLogPanel()">📋 로그</button>' in code:
    snapshot_ui = '<button class="header-btn btn-log-view" onclick="openLogPanel()">📄 로그 / 복구</button>'
    code = code.replace('<button class="header-btn" onclick="openLogPanel()">📋 로그</button>', snapshot_ui)

# 3. Fix map position
code = code.replace("margin-top: auto; margin-bottom: 0;", "margin-top: 15px; margin-bottom: 0;")

# Make sure APP_VERSION is bumped to 2.7.8
code = code.replace("const APP_VERSION = 'v2.7.7';", "const APP_VERSION = 'v2.7.8';")
code = code.replace(">v2.7.7</span></h1>", ">v2.7.8</span></h1>")

with open('index.html', 'w') as f:
    f.write(code)


# --- Fix Re.js ---
with open('apps_script/Re.js', 'r') as f:
    re_js = f.read()

# 1. formatMatingSheet: rowData[2] = c.subId
re_js = re_js.replace("rowData[2] = strainCNo;", "rowData[2] = c.subId;")

# 2. formatMatingSheet: Fix mergedText
# In formatMatingSheet, we have:
#       if (isGDone) {
#         sheet.getRange(b.start, 2, 1, 1).setValue(`${b.code}(G완)`);
#       }
#       sheet.getRange(b.start, 5, b.num, 1).setBackground(b.color); 
# Let's replace the whole blocks.forEach inside formatMatingSheet
mating_blocks_fix = """    blocks.forEach(b => {
      let sm = data.strainMap[b.code];
      let strainName = b.code;
      let isGDone = false;
      if (sm) {
        if (typeof sm === 'string') strainName = sm;
        else {
          if (sm.name) strainName = sm.name;
          isGDone = !!sm.g_done;
        }
      }
      if (isGDone) {
        sheet.getRange(b.start, 2, 1, 1).setValue(`${b.code}(G완)`);
      }
      
      let mergedText = `${strainName}\\n(${b.num})`;
      sheet.getRange(b.start, 5, 1, 1).setValue(mergedText);
      
      sheet.getRange(b.start, 5, b.num, 1).setBackground(b.color); 
      if (b.num > 1) sheet.getRange(b.start, 5, b.num, 1).merge().setVerticalAlignment('middle'); 
      sheet.getRange(b.start, 2, b.num, 1).setFontWeight('bold'); 
      sheet.getRange(b.start, 3, b.num, 8).setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    });"""
re_js = re.sub(
    r"    blocks\.forEach\(b => \{\n      let sm = data\.strainMap\[b\.code\];.*?sheet\.getRange\(b\.start, 3, b\.num, 8\)\.setBorder.*?\}\);",
    mating_blocks_fix,
    re_js,
    count=1,
    flags=re.DOTALL
)

with open('apps_script/Re.js', 'w') as f:
    f.write(re_js)

print("Bugs fixed")
