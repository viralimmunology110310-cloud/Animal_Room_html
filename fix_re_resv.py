import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

res_map_old = """      // 스트레인 기호 추출 로직 (A, C, D 등)
      if (rawStrain) {
         currentStrain = rawStrain;
      }
      
      if (currentStrain && cageNo && resv) {
         const key = currentStrain.toUpperCase() + '_' + cageNo;
         map[key] = resv;
      }
    });"""

res_map_new = """      if (rawStrain) {
         currentStrain = rawStrain;
      }
      
      let sex = String(row[3] || '').trim().toLowerCase();
      let head = String(row[4] || '').trim();
      let rawDob = String(row[5] || '').trim();
      
      let sanDob = rawDob.replace(/\\D/g, ''); // 2026. 06. 09. -> 20260609
      if (sanDob.length === 6) { sanDob = '20' + sanDob; }
      
      if (currentStrain && sex && head && sanDob && resv) {
         const key = currentStrain.toUpperCase() + '_' + sex + '_' + head + '_' + sanDob;
         map[key] = resv;
      }
    });"""

content = content.replace(res_map_old, res_map_new)

# Update formatMatingSheet and formatBreedingSheet to pass the right keys
mating_res_old = """    const resv = reservationMap[c.code + '_' + c.subId];"""
mating_res_new = """    const sanDobM = c.mDob ? String(c.mDob).replace(/\\D/g, '') : '';
    const sanDobF = c.fDob ? String(c.fDob).replace(/\\D/g, '') : '';
    let resv = reservationMap[c.code + '_m_' + c.mMale + '_' + sanDobM] || reservationMap[c.code + '_f_' + c.mFemale + '_' + sanDobF];
    if (!resv && c.mFemale && !sanDobF) {
       // fallback if DOB missing
       resv = reservationMap[c.code + '_f_' + c.mFemale + '_'];
    }"""
content = content.replace(mating_res_old, mating_res_new)

breeding_res_old = """    const resv = reservationMap[c.code + '_' + c.subId];"""
breeding_res_new = """    let sexChar = c.gender === 'male' ? 'm' : (c.gender === 'female' ? 'f' : '');
    const sanDob = c.bDob ? String(c.bDob).replace(/\\D/g, '') : '';
    const resv = reservationMap[c.code + '_' + sexChar + '_' + c.bCount + '_' + sanDob];"""
content = content.replace(breeding_res_old, breeding_res_new)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)

