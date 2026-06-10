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

target = """        };

                startTransaction();"""
replacement = """        };""" + "\n" + bad_block

content = content.replace(target, replacement)

with open('index.html', 'w') as f:
    f.write(content)
