import re

with open('index.html', 'r') as f:
    content = f.read()

bad_block = """
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

# Replace all back to startTransaction();
content = content.replace(bad_block, "        startTransaction();")

# Now selectively put it back ONLY in saveCage
save_cage_marker = "const isNew = !cages[info.id];"
save_cage_replacement = bad_block.strip() + "\n        " + save_cage_marker

content = content.replace("startTransaction();\n        " + save_cage_marker, save_cage_replacement)

# Also fix the floating button blocking clicks and F1
# We need to find the Guide button.
guide_btn_old = """<div class="shortcut-guide-btn" onclick="toggleShortcutModal()">⌨️ Guide (F1)</div>"""
# The user wants to hide the floating button.
guide_btn_new = """<div class="shortcut-guide-btn" onclick="toggleShortcutModal()" style="display:none;">⌨️ Guide (F1)</div>"""
content = content.replace(guide_btn_old, guide_btn_new)

# Add F1 listener
f1_listener = """    document.addEventListener('keydown', function(e) {
        if (e.key === 'F1') {
            e.preventDefault();
            toggleShortcutModal();
        }
    });"""
if "if (e.key === 'F1')" not in content:
    content = content.replace("document.addEventListener('DOMContentLoaded', () => {", "document.addEventListener('DOMContentLoaded', () => {\n" + f1_listener)

# Change version string to include (DEV)
version_old = "2.8"
version_new = "2.8 (DEV)"
content = content.replace("v" + version_old, "v" + version_new)
content = content.replace("v " + version_old, "v " + version_new)

with open('index.html', 'w') as f:
    f.write(content)

