function test() {
   // Simulated getReservationMap logic
   let data = [
      ["G", "1", "WT(29)", "f", "3", "2026.04.23", "", ""],
      ["", "2", "", "f", "3", "2026.04.25", "", ""],
      ["", "3", "", "f", "3", "2026.04.28", "", "예약이요"]
   ];
   let map = {};
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
      if (rawDob instanceof Date) {
         let y = rawDob.getFullYear();
         let m = String(rawDob.getMonth() + 1).padStart(2, '0');
         let d = String(rawDob.getDate()).padStart(2, '0');
         sanDob = y + m + d;
      } else {
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
      }
      
      if (currentStrain && sex && head && sanDob && resv) {
         const key = currentStrain.toUpperCase() + '_' + sex + '_' + head + '_' + sanDob;
         if (map[key]) {
             map[key] += ', ' + resv;
         } else {
             map[key] = resv;
         }
         console.log("Mapped key:", key, "->", map[key]);
      }
   });
   console.log("Final map:", map);
}
test();
