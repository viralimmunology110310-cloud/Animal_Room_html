import re

with open('index.html', 'r') as f:
    content = f.read()

# Update CSS for slide animation
css_old = """.chip-sub-row {
            display: flex; gap: 6px; align-items: center;
            background: rgba(255,255,255,0.03);
            border-left: 2px solid #ff453a;
            padding: 4px 8px;
            border-radius: 4px;
            margin-left: 4px;
        }"""
css_new = """.chip-sub-row {
            display: flex; gap: 6px; align-items: center;
            background: rgba(255,255,255,0.03);
            border-left: 2px solid #ff453a;
            padding: 0 8px;
            border-radius: 4px;
            margin-left: 4px;
            overflow: hidden;
            max-width: 0;
            opacity: 0;
            transition: max-width 0.3s ease, opacity 0.2s ease, padding 0.3s ease;
            white-space: nowrap;
        }
        .chip-sub-row.show {
            max-width: 300px;
            opacity: 1;
            padding: 4px 8px;
        }"""
content = content.replace(css_old, css_new)

# Update the JS to use classList instead of display='none'/'flex'
js_old_1 = "document.getElementById('gdone-sub').style.display = 'flex';"
js_new_1 = "document.getElementById('gdone-sub').classList.add('show');"
content = content.replace(js_old_1, js_new_1)

js_old_2 = "document.getElementById('gdone-sub').style.display = 'none';"
js_new_2 = "document.getElementById('gdone-sub').classList.remove('show');"
content = content.replace(js_old_2, js_new_2)

# Also fix the initial HTML to not have style="display:none"
html_old = """<div id="gdone-sub" class="chip-sub-row" style="display:none">"""
html_new = """<div id="gdone-sub" class="chip-sub-row">"""
content = content.replace(html_old, html_new)

with open('index.html', 'w') as f:
    f.write(content)

