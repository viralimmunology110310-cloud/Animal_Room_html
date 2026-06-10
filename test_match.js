const fs = require('fs');

function getReservationMap() {
  const map = {};
  // Mock data representing exactly what's on the sheet
  const data = [
      // Strain, Cage No, Genotype, Sex, Head, DOB, weaning, Reservation1, Reservation2, Reservation3, Reservation4
      ["G (1)", "1", "WT(29)", "f", "3", "2026.04.28", "", "예약이요", "", "", ""],
      ["AC", "2", "Nlrp4a", "m", "1", "2026.04.05", "", "", "테스트", "", ""],
      ["g", "3", "", "m", "2", "2026.04.28", "", "예약", "", "", ""],
      ["", "4", "", "f", "3", "2026.04.28", "", "G의 빈칸 예약", "", "", ""]
  ];
  
  let currentStrain = '';
  data.forEach(row => {
    let rawStrain = String(row[0] || '').trim();
    
    let vals = [];
    for (let c = 7; c <= 10; c++) {
      let v = String(row[c] || '').trim();
      if (v) vals.push(v);
    }
    let resv = vals.join(', ');
    
    if (rawStrain) {
       currentStrain = rawStrain.replace(/\s*\([^)]*\)\s*/g, '');
    }
    
    let sex = String(row[3] || '').trim().toLowerCase();
    let head = String(row[4] || '').trim();
    let rawDob = row[5];
    let sanDob = '';
    rawDob = String(rawDob || '').trim();
    let parts = rawDob.split(/[\/\-.]+/).filter(Boolean);
    if (parts.length === 3) {
       let y = parts[0].length === 2 ? '20' + parts[0] : parts[0];
       let m = parts[1].padStart(2, '0');
       let d = parts[2].padStart(2, '0');
       sanDob = y + m + d;
    } else {
       sanDob = rawDob.replace(/\D/g, '');
       if (sanDob.length === 6) sanDob = '20' + sanDob;
    }
    
    if (currentStrain && sex && head && sanDob && resv) {
       const key = currentStrain.toUpperCase() + '_' + sex + '_' + head + '_' + sanDob;
       if (map[key]) {
           map[key] += ', ' + resv;
       } else {
           map[key] = resv;
       }
       console.log("Reservation Key Generated:", key, "=>", resv);
    }
  });
  return map;
}

const map = getReservationMap();
console.log("\nFinal Map:", map);

// Test matching against breeding logic
console.log("\n--- Matching Test ---");
const testCages = [
  { code: 'G', gender: 'female', bCount: '3', bDob: '2026-04-28' },
  { code: 'g', gender: 'male', bCount: '2', bDob: '2026.04.28' },
  { code: 'AC', gender: 'male', bCount: '1', bDob: '2026-04-05' }
];

testCages.forEach(c => {
  let codeUp = String(c.code || '').toUpperCase();
  let sexChar = c.gender === 'male' ? 'm' : (c.gender === 'female' ? 'f' : '');
  
  let rawDob = c.bDob;
  rawDob = String(rawDob || '').trim();
  let parts = rawDob.split(/[\/\-.]+/).filter(Boolean);
  let sanDob = '';
  if (parts.length === 3) {
     let y = parts[0].length === 2 ? '20' + parts[0] : parts[0];
     let m = parts[1].padStart(2, '0');
     let d = parts[2].padStart(2, '0');
     sanDob = y + m + d;
  } else {
     sanDob = rawDob.replace(/\D/g, '');
     if (sanDob.length === 6) sanDob = '20' + sanDob;
  }
  
  let key = codeUp + '_' + sexChar + '_' + (c.bCount||0) + '_' + sanDob;
  console.log("Checking Dev Cage Key:", key, "=> Found:", map[key]);
});

