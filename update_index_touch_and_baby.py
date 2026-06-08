import re

with open('index.html', 'r') as f:
    code = f.read()

# 1. Update Baby note regex in index.html
code = re.sub(
    r"const regex = \/Baby \\d\+마리\\(\(\\d\{1,2\}\)\/(\\d\{1,2\}\)\\)\/g;",
    r"const regex = /Baby\\s*\\d+\\s*마리\\s*\\(\\s*(\\d{1,2})\\s*\\/\\s*(\\d{1,2})\\s*\\)/g;",
    code
)

# 2. Update formatDateDots in index.html
format_date_old = """        function formatDateDots(d) {
            if (!d) return '';
            const dt = new Date(d);
            if (isNaN(dt)) return d.replace(/-/g, '.');
            return `${dt.getFullYear()}.${String(dt.getMonth()+1).padStart(2,'0')}.${String(dt.getDate()).padStart(2,'0')}`;
        }"""
format_date_new = """        function formatDateDots(d) {
            if (!d) return '';
            const dt = new Date(d);
            if (isNaN(dt)) return d.replace(/-/g, '.');
            return `${dt.getFullYear()}.${dt.getMonth()+1}.${dt.getDate()}`;
        }"""
code = code.replace(format_date_old, format_date_new)

# 3. Add touch row toggling logic and inject into TRs
touch_js = """
    let activeTouchCageId = null;
    window.toggleTouchRow = function(cageId) {
        const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
        if (!isTouch) return;
        
        if (activeTouchCageId && activeTouchCageId !== cageId) {
            unhoverSidebarRow(activeTouchCageId);
        }
        
        if (activeTouchCageId === cageId) {
            unhoverSidebarRow(cageId);
            activeTouchCageId = null;
        } else {
            activeTouchCageId = cageId;
            hoverSidebarRow(cageId);
        }
    };
"""
if "let activeTouchCageId = null;" not in code:
    code = code.replace("    window.hoverSidebarRow = function(cageId) {", touch_js + "\n    window.hoverSidebarRow = function(cageId) {")

code = code.replace(
    """<tr id="row-mating-${c.id}" onmouseenter="hoverSidebarRow('${c.id}')" onmouseleave="unhoverSidebarRow('${c.id}')">""",
    """<tr id="row-mating-${c.id}" onmouseenter="hoverSidebarRow('${c.id}')" onmouseleave="unhoverSidebarRow('${c.id}')" onclick="toggleTouchRow('${c.id}')">"""
)
code = code.replace(
    """<tr id="row-breeding-${c.id}" onmouseenter="hoverSidebarRow('${c.id}')" onmouseleave="unhoverSidebarRow('${c.id}')">""",
    """<tr id="row-breeding-${c.id}" onmouseenter="hoverSidebarRow('${c.id}')" onmouseleave="unhoverSidebarRow('${c.id}')" onclick="toggleTouchRow('${c.id}')">"""
)

# 4. Make splitter touch-friendly
splitter_old = """            splitter.addEventListener('mousedown', (e) => {
                isDragging = true;
                window._splitterDragging = true;
                startX = e.clientX;
                startWidth = sheetPane.getBoundingClientRect().width;
                splitter.classList.add('dragging');
                document.body.style.cursor = 'col-resize';
                e.preventDefault();
            });
            
            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                const diff = startX - e.clientX; // moving left increases right pane width
                let newWidth = startWidth + diff;
                newWidth = Math.max(250, Math.min(1000, newWidth)); // min 250, max 1000
                sheetPane.style.setProperty('--sheet-width', newWidth + 'px');
                sheetPane.style.width = newWidth + 'px';
            });
            
            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    window._splitterDragging = false;
                    splitter.classList.remove('dragging');
                    document.body.style.cursor = '';
                }
            });"""

splitter_new = """            splitter.addEventListener('mousedown', (e) => {
                isDragging = true;
                window._splitterDragging = true;
                startX = e.clientX;
                startWidth = sheetPane.getBoundingClientRect().width;
                splitter.classList.add('dragging');
                document.body.style.cursor = 'col-resize';
                e.preventDefault();
            });
            
            splitter.addEventListener('touchstart', (e) => {
                const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
                if (!isTouch) return;
                isDragging = true;
                window._splitterDragging = true;
                startX = e.touches[0].clientX;
                startWidth = sheetPane.getBoundingClientRect().width;
                splitter.classList.add('dragging');
                document.body.style.cursor = 'col-resize';
            }, {passive: true});

            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                const diff = startX - e.clientX;
                let newWidth = startWidth + diff;
                newWidth = Math.max(250, Math.min(1000, newWidth));
                sheetPane.style.setProperty('--sheet-width', newWidth + 'px');
                sheetPane.style.width = newWidth + 'px';
            });
            
            document.addEventListener('touchmove', (e) => {
                if (!isDragging) return;
                const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
                if (!isTouch) return;
                const diff = startX - e.touches[0].clientX;
                let newWidth = startWidth + diff;
                newWidth = Math.max(250, Math.min(1000, newWidth));
                sheetPane.style.setProperty('--sheet-width', newWidth + 'px');
                sheetPane.style.width = newWidth + 'px';
            }, {passive: true});

            const stopDrag = () => {
                if (isDragging) {
                    isDragging = false;
                    window._splitterDragging = false;
                    splitter.classList.remove('dragging');
                    document.body.style.cursor = '';
                }
            };
            document.addEventListener('mouseup', stopDrag);
            document.addEventListener('touchend', stopDrag);"""

code = code.replace(splitter_old, splitter_new)

code = code.replace("const APP_VERSION = 'v2.7.10';", "const APP_VERSION = 'v2.7.11';")
code = code.replace(">v2.7.10</span></h1>", ">v2.7.11</span></h1>")

with open('index.html', 'w') as f:
    f.write(code)

# --- Fix Re.js ---
with open('apps_script/Re.js', 'r') as f:
    re_js = f.read()

mating_notes_new_safe = """      if (c.notes) {
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

re_js = re.sub(
    r"      let builder = SpreadsheetApp\.newRichTextValue\(\)\.setText\(c\.notes\);.*?sheet\.getRange\(b\.start, 7, b\.num, 1\)\.setRichTextValue\(builder\.build\(\)\);",
    mating_notes_new_safe,
    re_js,
    flags=re.DOTALL
)

with open('apps_script/Re.js', 'w') as f:
    f.write(re_js)

print("Updated baby logic and touch support")
