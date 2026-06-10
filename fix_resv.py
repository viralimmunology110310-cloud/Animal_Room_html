import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

# Fix Mating
mating_old = """    const sanDobM = parseDob(c.mDob);
    const sanDobF = parseDob(c.fDob);
    let resv = reservationMap[c.code + '_m_' + c.mMale + '_' + sanDobM] || reservationMap[c.code + '_f_' + c.mFemale + '_' + sanDobF];
    if (!resv && c.mFemale && !sanDobF) {
       // fallback if DOB missing
       resv = reservationMap[c.code + '_f_' + c.mFemale + '_'];
    }"""
mating_new = """    const sanDobM = parseDob(c.mDob);
    const sanDobF = parseDob(c.fDob);
    let codeUp = String(c.code || '').toUpperCase();
    let resv = reservationMap[codeUp + '_m_' + c.mMale + '_' + sanDobM] || reservationMap[codeUp + '_f_' + c.mFemale + '_' + sanDobF];
    if (!resv && c.mFemale && !sanDobF) {
       resv = reservationMap[codeUp + '_f_' + c.mFemale + '_'];
    }"""
content = content.replace(mating_old, mating_new)

# Fix Breeding
breeding_old = """    const sanDobM = parseDob(c.mDob);
    const sanDobF = parseDob(c.fDob);
    let resv = reservationMap[c.code + '_m_' + c.mMale + '_' + sanDobM] || reservationMap[c.code + '_f_' + c.mFemale + '_' + sanDobF];
    if (!resv && c.mFemale && !sanDobF) {
       // fallback if DOB missing
       resv = reservationMap[c.code + '_f_' + c.mFemale + '_'];
    }"""
breeding_new = """    let codeUp = String(c.code || '').toUpperCase();
    let sexChar = c.gender === 'male' ? 'm' : (c.gender === 'female' ? 'f' : '');
    let resv = reservationMap[codeUp + '_' + sexChar + '_' + (c.bCount||0) + '_' + sanDob];
    if (!resv && !sanDob) {
       resv = reservationMap[codeUp + '_' + sexChar + '_' + (c.bCount||0) + '_'];
    }"""
content = content.replace(breeding_old, breeding_new)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
