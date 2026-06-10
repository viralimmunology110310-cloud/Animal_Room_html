import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

reservation_func = """// ── 예약 시트 데이터 가져오기 ──
function getReservationMap() {
  const map = {};
  try {
    const resSS = SpreadsheetApp.openById('1AAPiUrITICfZQQHhUtAHAhqg0a5GTabuPeqbJyL04mU');
    const resSheet = resSS.getSheetByName('mouse reservation');
    if (!resSheet) return map;
    
    // 데이터 범위: A열(Strain) ~ H열(Reservation)
    const data = resSheet.getRange('A2:H' + Math.max(2, resSheet.getLastRow())).getValues();
    
    let currentStrain = '';
    data.forEach(row => {
      let rawStrain = String(row[0] || '').trim();
      let cageNo = String(row[1] || '').trim();
      let resv = String(row[7] || '').trim();
      
      // 스트레인 기호 추출 로직 (A, C, D 등)
      if (rawStrain) {
         currentStrain = rawStrain;
      }
      
      if (currentStrain && cageNo && resv) {
         const key = currentStrain.toUpperCase() + '_' + cageNo;
         map[key] = resv;
      }
    });
  } catch(e) {
    console.error('Reservation fetch error: ' + e);
  }
  return map;
}
"""

if "function getReservationMap()" not in content:
    content = content + "\n\n" + reservation_func

# In formatMatingSheet, pass reservationMap
mating_sig_old = "function formatMatingSheet(ss, data) {"
mating_sig_new = """function formatMatingSheet(ss, data, reservationMap) {
  reservationMap = reservationMap || {};"""
content = content.replace(mating_sig_old, mating_sig_new)

# In formatBreedingSheet, pass reservationMap
breeding_sig_old = "function formatBreedingSheet(ss, data) {"
breeding_sig_new = """function formatBreedingSheet(ss, data, reservationMap) {
  reservationMap = reservationMap || {};"""
content = content.replace(breeding_sig_old, breeding_sig_new)

# In formatMatingSheet, inject reservation string
mating_notes_old = "    rowData[8] = c.notes || '';"
mating_notes_new = """    let note = c.notes || '';
    const resv = reservationMap[c.code + '_' + c.subId];
    if (resv) note = (note ? note + '\\n' : '') + '[예약: ' + resv + ']';
    rowData[8] = note;"""
content = content.replace(mating_notes_old, mating_notes_new)

# In formatBreedingSheet, inject reservation string
breeding_notes_old = "    rowData[7] = c.notes || '';"
breeding_notes_new = """    let note = c.notes || '';
    const resv = reservationMap[c.code + '_' + c.subId];
    if (resv) note = (note ? note + '\\n' : '') + '[예약: ' + resv + ']';
    rowData[7] = note;"""
content = content.replace(breeding_notes_old, breeding_notes_new)

# Now update the main entry points (doPost, doGet, syncFromSheetButton, etc.)
# We need to fetch getReservationMap() and pass it.
# They are called as `formatMatingSheet(ss, data);`
calls_to_replace = ["formatMatingSheet(ss, data);", "formatBreedingSheet(ss, data);"]
# In syncFromSheetButton:
sync_old = """  // 시트 다시 그리기
  formatMatingSheet(ss, data);
  formatBreedingSheet(ss, data);"""
sync_new = """  // 예약 시트 연동 및 시트 다시 그리기
  const reservationMap = getReservationMap();
  formatMatingSheet(ss, data, reservationMap);
  formatBreedingSheet(ss, data, reservationMap);"""
content = content.replace(sync_old, sync_new)

do_post_old = """      formatMatingSheet(ss, data);
      formatBreedingSheet(ss, data);"""
do_post_new = """      const reservationMap = getReservationMap();
      formatMatingSheet(ss, data, reservationMap);
      formatBreedingSheet(ss, data, reservationMap);"""
content = content.replace(do_post_old, do_post_new)

do_get_old = """    formatMatingSheet(ss, data);
    formatBreedingSheet(ss, data);"""
do_get_new = """    const reservationMap = getReservationMap();
    formatMatingSheet(ss, data, reservationMap);
    formatBreedingSheet(ss, data, reservationMap);"""
content = content.replace(do_get_old, do_get_new)


with open('apps_script/Re.js', 'w') as f:
    f.write(content)
