import re

with open('apps_script/Re.js', 'r') as f:
    lines = f.readlines()

in_breeding = False
new_lines = []
for line in lines:
    if "function formatBreedingSheet" in line:
        in_breeding = True
    
    if in_breeding and "const sanDobM = parseDob(c.mDob);" in line:
        pass # skip
    elif in_breeding and "const sanDobF = parseDob(c.fDob);" in line:
        pass # skip
    elif in_breeding and "let codeUp = String(c.code || '').toUpperCase();" in line:
        pass # skip
    elif in_breeding and "let resv = reservationMap[codeUp + '_m_' + c.mMale + '_' + sanDobM] || reservationMap[codeUp + '_f_' + c.mFemale + '_' + sanDobF];" in line:
        new_lines.append("    let codeUp = String(c.code || '').toUpperCase();\n")
        new_lines.append("    let sexChar = c.gender === 'male' ? 'm' : (c.gender === 'female' ? 'f' : '');\n")
        new_lines.append("    const sanDob = parseDob(c.bDob);\n")
        new_lines.append("    let resv = reservationMap[codeUp + '_' + sexChar + '_' + (c.bCount||0) + '_' + sanDob];\n")
    elif in_breeding and "resv = reservationMap[codeUp + '_f_' + c.mFemale + '_'];" in line:
        new_lines.append("       resv = reservationMap[codeUp + '_' + sexChar + '_' + (c.bCount||0) + '_'];\n")
    else:
        new_lines.append(line)

with open('apps_script/Re.js', 'w') as f:
    f.writelines(new_lines)
