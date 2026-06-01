function doPost(e) {
  try {
    const rawData = e.postData.contents;
    const data = JSON.parse(rawData);

    if (data.action === 'save') {
      const ss = SpreadsheetApp.getActiveSpreadsheet();

      // DB 저장 (히든 시트 A1에 JSON 전체 저장)
      let dbSheet = ss.getSheetByName('DB');
      if (!dbSheet) {
        dbSheet = ss.insertSheet('DB');
        dbSheet.hideSheet();
      }
      dbSheet.getRange('A1').setValue(rawData);

      // Strain Map 시트 포맷팅 및 업데이트
      updateStrainMapSheet(ss, data);

      // Mating 시트 포맷팅 (노란색 케이지)
      formatMatingSheet(ss, data);

      // Breeding 시트 포맷팅 (흰색 케이지)
      formatBreedingSheet(ss, data);
      
      // 로그 시트 포맷팅
      formatLogSheet(ss, data);

      return ContentService.createTextOutput(JSON.stringify({ status: 'success' }))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const dbSheet = ss.getSheetByName('DB');
  if (dbSheet) {
    const rawData = dbSheet.getRange('A1').getValue();
    if (rawData) {
      return ContentService.createTextOutput(rawData)
        .setMimeType(ContentService.MimeType.JSON);
    }
  }
  return ContentService.createTextOutput(JSON.stringify({ cages: [], logs: [] }))
    .setMimeType(ContentService.MimeType.JSON);
}

// ─────────────────────────────────────────────────────────────
// 이하 포맷팅 함수들
// ─────────────────────────────────────────────────────────────

// Strain 정렬 함수: 문자 -> 숫자
function sortStrainKeys(keys) {
  return keys.sort((a, b) => {
    let aMatch = a.match(/^([A-Za-z]+)(\d*)$/);
    let bMatch = b.match(/^([A-Za-z]+)(\d*)$/);
    if (!aMatch || !bMatch) return a.localeCompare(b);
    let aAlpha = aMatch[1];
    let bAlpha = bMatch[1];
    if (aAlpha.length !== bAlpha.length) return aAlpha.length - bAlpha.length;
    if (aAlpha !== bAlpha) return aAlpha.localeCompare(bAlpha);
    return (parseInt(aMatch[2])||0) - (parseInt(bMatch[2])||0);
  });
}

function updateStrainMapSheet(ss, data) {
  if (!data.strainMap) return;
  let sheet = ss.getSheetByName('Strain Map');
  if (!sheet) {
    sheet = ss.insertSheet('Strain Map');
  }
  
  // 항상 Firebase의 strainMap을 시트에 덮어쓰기 (Firebase가 마스터)
  sheet.clear();
  sheet.getRange('A1:C1').setValues([['기호(알파벳)', 'Strain 이름', 'G완료 여부(O/X)']]).setFontWeight('bold').setBackground('#f3f3f3');
  sheet.setColumnWidth(1, 100);
  sheet.setColumnWidth(2, 200);
  sheet.setColumnWidth(3, 120);
  
  const keys = sortStrainKeys(Object.keys(data.strainMap));
  const rows = keys.map(k => {
    const val = data.strainMap[k];
    let name = '', g_done = 'X';
    if (typeof val === 'string') name = val;
    else { name = val.name || ''; g_done = val.g_done ? 'O' : 'X'; }
    return [k, name, g_done];
  });
  if (rows.length > 0) sheet.getRange(2, 1, rows.length, 3).setValues(rows);
}

function formatDateDots(dateStr) {
  if (!dateStr) return '';
  return dateStr.replace(/-/g, '.');
}

function isSameWeek(ts1, ts2) {
  if (!ts1 || !ts2) return false;
  let d1 = new Date(ts1);
  let d2 = new Date(ts2);
  let day1 = d1.getDay() || 7;
  let d1Mon = new Date(d1.getFullYear(), d1.getMonth(), d1.getDate() - day1 + 1);
  let day2 = d2.getDay() || 7;
  let d2Mon = new Date(d2.getFullYear(), d2.getMonth(), d2.getDate() - day2 + 1);
  return d1Mon.getTime() === d2Mon.getTime();
}

const STRAIN_COLORS = [
  '#fce5cd', '#d9ead3', '#c9daf8', '#ead1dc', '#fff2cc', '#e6b8af', '#d0e0e3', '#d9d2e9'
];

function getCageDay(cage, dayMap, wtRanges) {
  if (dayMap && dayMap[cage.code]) {
    for (let day in dayMap[cage.code]) {
      const ranges = dayMap[cage.code][day];
      const subNum = parseInt(cage.subId);
      if (!isNaN(subNum)) {
        for (let r of ranges) {
          if (subNum >= r[0] && subNum <= r[1]) return day;
        }
      }
    }
  }
  // wtRanges 확인
  if (wtRanges && cage.code === 'WT') {
    const subNum = parseInt(cage.subId);
    if (!isNaN(subNum)) {
      for (let w of wtRanges) {
        if (subNum >= w.start && subNum <= w.end) return w.day;
      }
    }
  }
  return '';
}

function formatMatingSheet(ss, data) {
  let sheet = ss.getSheetByName('Mating');
  if (!sheet) sheet = ss.insertSheet('Mating');
  sheet.clear();
  
  const now = new Date();
  const todayStr = `${now.getFullYear()}.${String(now.getMonth()+1).padStart(2,'0')}.${String(now.getDate()).padStart(2,'0')}`;
  
  sheet.getRange('B1').setValue(todayStr).setFontWeight('bold');
  sheet.getRange('C1:J1').merge().setValue('Mating').setHorizontalAlignment('center').setFontWeight('bold').setFontSize(14);
  
  const headers = ['No.', 'C.no.', 'Strain', 'male', 'female', 'D.O.B', 'D.O.M', 'other'];
  sheet.getRange(2, 3, 1, headers.length).setValues([headers]).setFontWeight('bold').setHorizontalAlignment('center');

  const matingCages = data.cages.filter(c => c.type === 'mating');
  matingCages.sort((a, b) => {
    let aCode = a.code || '';
    let bCode = b.code || '';
    if (aCode.length !== bCode.length) return aCode.length - bCode.length;
    if (aCode !== bCode) return aCode.localeCompare(bCode);
    return (parseInt(a.subId)||0) - (parseInt(b.subId)||0);
  });

  const output = [];
  const richTexts = [];
  const bColors = [];
  let currentStrainCode = null;
  let globalNo = 1;
  let strainCNo = 0;
  let colorIdx = -1;
  let blocks = [];
  let currentBlock = null;

  matingCages.forEach((c, idx) => {
    const isFirstStrain = (c.code !== currentStrainCode);
    if (isFirstStrain) {
      currentStrainCode = c.code;
      strainCNo = 1;
      colorIdx = (colorIdx + 1) % STRAIN_COLORS.length;
      if (currentBlock) blocks.push(currentBlock);
      currentBlock = { start: 3 + idx, num: 1, color: STRAIN_COLORS[colorIdx], code: c.code };
    } else {
      strainCNo++;
      currentBlock.num++;
    }

    const bCol = isFirstStrain ? c.code : '';
    let sm = data.strainMap[c.code];
    let strainName = c.code;
    let isGDone = false;
    if (sm) {
      if (typeof sm === 'string') strainName = sm;
      else {
        if (sm.name) strainName = sm.name;
        isGDone = !!sm.g_done;
      }
    }

    let formatGeno = (count, geno) => {
      if (!count) return '';
      let g = (geno || '').toLowerCase();
      if (g.includes('homo') || g.includes('het')) {
        return `${count}(${geno})`;
      }
      return `${count}`;
    };
    let mTxt = formatGeno(c.mMale, c.mGeno);
    let fTxt = formatGeno(c.mFemale, c.fGeno);
    let mD = c.mDob ? new Date(c.mDob) : new Date(0);
    let fD = c.fDob ? new Date(c.fDob) : new Date(0);
    let youngerDob = '';
    if (c.mDob && c.fDob) youngerDob = (mD > fD) ? c.mDob : c.fDob;
    else if (c.mDob) youngerDob = c.mDob;
    else if (c.fDob) youngerDob = c.fDob;
    let dobTxt = formatDateDots(youngerDob);

    let rowData = new Array(15).fill('');
    rowData[0] = bCol;
    rowData[1] = globalNo++;
    rowData[2] = c.subId;
    rowData[3] = strainName;
    rowData[4] = mTxt;
    rowData[5] = fTxt;
    rowData[6] = dobTxt;
    rowData[7] = formatDateDots(c.dom);
    rowData[8] = c.notes || '';
    rowData[9] = isGDone ? '' : `${c.code}${c.subId}`;
    rowData[14] = c.id; // P열(16번째)
    output.push(rowData);

    let day = getCageDay(c, data.dayMap, data.wtRanges);
    let dayColor = '#ffffff';
    if (day === 'Mon') dayColor = '#fff2cc';
    else if (day === 'Tue') dayColor = '#d9ead3';
    else if (day === 'Wed') dayColor = '#d9d2e9';
    bColors.push([dayColor]);

    let noteColor = '#000000';
    if (c.notes) {
      if (c.noteUpdated && isSameWeek(c.noteUpdated, now.getTime())) {
        noteColor = '#FF0000';
      } else {
        noteColor = '#0000FF';
      }
    }
    richTexts.push(noteColor);
  });
  if (currentBlock) blocks.push(currentBlock);

  if (output.length > 0) {
    sheet.getRange(3, 2, output.length, 15).setValues(output).setHorizontalAlignment('center');
    sheet.getRange(3, 10, output.length, 1).setFontColors(richTexts.map(c => [c])).setHorizontalAlignment('left');
    sheet.getRange(3, 2, output.length, 1).setBackgrounds(bColors);
    
    blocks.forEach(b => {
      let sm = data.strainMap[b.code];
      let strainName = b.code;
      let isGDone = false;
      if (sm) {
        if (typeof sm === 'string') strainName = sm;
        else {
          if (sm.name) strainName = sm.name;
          isGDone = !!sm.g_done;
        }
      }
      
      let mergedText = `${strainName}\n(${b.num})`;
      sheet.getRange(b.start, 5, 1, 1).setValue(mergedText);

      if (isGDone) {
        sheet.getRange(b.start, 2, 1, 1).setValue(`${b.code}(G완)`);
      }
      sheet.getRange(b.start, 5, b.num, 1).setBackground(b.color); // Strain 열(E)만 배경색
      if (b.num > 1) sheet.getRange(b.start, 5, b.num, 1).merge().setVerticalAlignment('middle'); // Strain 열(E) 병합
      
      sheet.getRange(b.start, 2, b.num, 1).setFontWeight('bold'); // B열 굵게
      
      // 테두리: 외곽선 전체 + 내부 세로선만 (가로선 제외). B열(2) 제외하고 C열(3)부터 8칸(C~J)만 적용
      sheet.getRange(b.start, 3, b.num, 8).setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    });
    
    // No. 열(C열)은 통째로 내부 가로선 제거 (strain 간의 테두리도 없앰)
    sheet.getRange(3, 3, output.length, 1).setBorder(true, null, true, null, null, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  }

  // Set column widths for Mating sheet (B to J)
  const matingWidths = [87, 59, 47, 185, 89, 82, 97, 87, 410];
  matingWidths.forEach((w, i) => sheet.setColumnWidth(2 + i, w));

  // Set borders for rows 1 and 2 (C to J)
  sheet.getRange(1, 3, 2, 8).setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  
  sheet.hideColumns(16); sheet.hideColumns(11); // P열, K열 숨기기
  // sheet.autoResizeColumns(2, 10); // 고정 너비 사용으로 인해 비활성화
}

function formatBreedingSheet(ss, data) {
  let sheet = ss.getSheetByName('Breeding');
  if (!sheet) sheet = ss.insertSheet('Breeding');
  sheet.clear();

  const now = new Date();
  const todayStr = `${now.getFullYear()}.${String(now.getMonth()+1).padStart(2,'0')}.${String(now.getDate()).padStart(2,'0')}`;
  
  sheet.getRange('B1').setValue(todayStr).setFontWeight('bold');
  sheet.getRange('C1:I1').merge().setValue('Breeding').setHorizontalAlignment('center').setFontWeight('bold').setFontSize(14);
  
  const headers = ['No.', 'C.no.', 'Strain', 'sex', 'head', 'D.O.B', 'other'];
  sheet.getRange(2, 3, 1, headers.length).setValues([headers]).setFontWeight('bold').setHorizontalAlignment('center');

  const breedingCages = data.cages.filter(c => c.type === 'breeding' || c.type === 'empty');
  breedingCages.sort((a, b) => {
    let aCode = a.code || '';
    let bCode = b.code || '';
    if (aCode.length !== bCode.length) return aCode.length - bCode.length;
    if (aCode !== bCode) return aCode.localeCompare(bCode);
    return (parseInt(a.subId)||0) - (parseInt(b.subId)||0);
  });

  const output = [];
  const richTexts = [];
  const bColors = [];
  let currentStrainCode = null;
  let globalNo = 1;
  let strainCNo = 0;
  let colorIdx = -1;
  let blocks = [];
  let currentBlock = null;

  breedingCages.forEach((c, idx) => {
    const isFirstStrain = (c.code !== currentStrainCode);
    if (isFirstStrain) {
      currentStrainCode = c.code;
      strainCNo = 1;
      colorIdx = (colorIdx + 1) % STRAIN_COLORS.length;
      if (currentBlock) blocks.push(currentBlock);
      currentBlock = { 
        start: 3 + idx, num: 1, color: STRAIN_COLORS[colorIdx], code: c.code,
        totalHeads: parseInt(c.bCount) || 0,
        g_pre: 0, g_done_heads: 0
      };
    } else {
      strainCNo++;
      currentBlock.num++;
      currentBlock.totalHeads += parseInt(c.bCount) || 0;
    }
    if (c.notes && c.notes.includes('G전')) currentBlock.g_pre += parseInt(c.bCount) || 0;
    else if (c.notes && c.notes.includes('G완')) currentBlock.g_done_heads += parseInt(c.bCount) || 0;

    const bCol = isFirstStrain ? c.code : '';
    let sm = data.strainMap[c.code];
    let strainName = c.code;
    let isGDone = false;
    if (sm) {
      if (typeof sm === 'string') strainName = sm;
      else {
        if (sm.name) strainName = sm.name;
        isGDone = !!sm.g_done;
      }
    }
    let sex = '?';
    if (c.gender === 'male') sex = 'm';
    else if (c.gender === 'female') sex = 'f';

    let rowData = new Array(15).fill('');
    rowData[0] = bCol;
    rowData[1] = globalNo++;
    rowData[2] = strainCNo;
    rowData[3] = strainName;
    rowData[4] = sex;
    rowData[5] = c.bCount;
    rowData[6] = formatDateDots(c.bDob);
    rowData[7] = c.notes || '';
    rowData[8] = isGDone ? '' : `${c.code}${c.subId}`;
    rowData[14] = c.id; // P열(16)
    output.push(rowData);

    let day = getCageDay(c, data.dayMap, data.wtRanges);
    let dayColor = '#ffffff';
    if (day === 'Mon') dayColor = '#fff2cc';
    else if (day === 'Tue') dayColor = '#d9ead3';
    else if (day === 'Wed') dayColor = '#d9d2e9';
    bColors.push([dayColor]);

    let color = '#000000';
    if (c.notes) {
      if (c.notes.includes('G완')) color = '#FF0000';
      else if (c.notes.includes('G전')) color = '#0000FF';
    }
    richTexts.push(color);
  });
  if (currentBlock) blocks.push(currentBlock);

  if (output.length > 0) {
    sheet.getRange(3, 2, output.length, 15).setValues(output).setHorizontalAlignment('center');
    sheet.getRange(3, 9, output.length, 1).setFontColors(richTexts.map(c => [c]));
    sheet.getRange(3, 10, output.length, 1).setHorizontalAlignment('left');
    sheet.getRange(3, 2, output.length, 1).setBackgrounds(bColors);
    

    blocks.forEach(b => {
      let sm = data.strainMap[b.code];
      let strainName = b.code;
      let isGDone = false;
      if (sm) {
        if (typeof sm === 'string') strainName = sm;
        else {
          if (sm.name) strainName = sm.name;
          isGDone = !!sm.g_done;
        }
      }
      
      let mergedText = '';
      if (isGDone) {
        mergedText = `${strainName}\n(${b.totalHeads})`;
        sheet.getRange(b.start, 2, 1, 1).setValue(`${b.code}(G완)`);
      } else {
        mergedText = `${strainName}\n(G전: ${b.g_pre} / G완: ${b.g_done_heads})`;
      }
      
      sheet.getRange(b.start, 5, 1, 1).setValue(mergedText);
      sheet.getRange(b.start, 5, b.num, 1).setBackground(b.color); // Strain 열(E)만 배경색
      if (b.num > 1) sheet.getRange(b.start, 5, b.num, 1).merge().setVerticalAlignment('middle'); // Strain 열(E) 병합
      
      sheet.getRange(b.start, 2, b.num, 1).setFontWeight('bold'); // B열 굵게

      
      // 테두리: 외곽선 전체 + 내부 세로선만 (가로선 제외). B열(2) 제외하고 C열(3)부터 7칸(C~I)만 적용
      sheet.getRange(b.start, 3, b.num, 7).setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    });
    
    // No. 열(C열)은 통째로 내부 가로선 제거 (strain 간의 테두리도 없앰)
    sheet.getRange(3, 3, output.length, 1).setBorder(true, null, true, null, null, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  }

  // Set column widths for Breeding sheet (B to J)
  const breedingWidths = [100, 76, 47, 122, 34, 44, 87, 168, 82];
  breedingWidths.forEach((w, i) => sheet.setColumnWidth(2 + i, w));

  // Set borders for rows 1 and 2 (C to I)
  sheet.getRange(1, 3, 2, 7).setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    
    // P열 숨기기
    sheet.hideColumns(16);
    // sheet.autoResizeColumns(2, 9); // 고정 너비 사용으로 인해 비활성화
}

// ── 구글 시트 전용 메뉴 추가 ──

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🐭 Animal Room')
      .addItem('🔄 시트 새로고침 (매칭표 적용)', 'syncFromSheetButton')
      .addItem('🗑️ 로그 초기화', 'clearLogsButton')
      .addToUi();
}


function syncFromSheetButton() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const dbSheet = ss.getSheetByName('DB');
  if (!dbSheet) {
    SpreadsheetApp.getUi().alert('DB 시트가 없습니다. 사이트에서 먼저 동기화를 진행해주세요.');
    return;
  }
  
  const rawData = dbSheet.getRange('A1').getValue();
  if (!rawData) {
    SpreadsheetApp.getUi().alert('DB 데이터가 비어있습니다.');
    return;
  }
  
  let data;
  try {
    data = JSON.parse(rawData);
  } catch(e) {
    SpreadsheetApp.getUi().alert('DB 데이터를 읽는 중 오류가 발생했습니다.');
    return;
  }
  // Strain Map 시트에서 최신 데이터를 읽어오고 정렬합니다.
  const smSheet = ss.getSheetByName('Strain Map');
  if (smSheet) {
    const lastRow = smSheet.getLastRow();
    if (lastRow > 1) {
      const smData = smSheet.getRange(2, 1, lastRow - 1, 3).getValues();
      const newStrainMap = {};
      smData.forEach(row => {
        if (row[0] && row[1]) {
          const g_done = String(row[2]).trim().toUpperCase() === 'O';
          newStrainMap[String(row[0]).trim()] = { name: String(row[1]).trim(), g_done };
        }
      });
      if (Object.keys(newStrainMap).length > 0) {
        data.strainMap = newStrainMap; // 새로 읽어온 맵으로 덮어쓰기
        // 시트도 다시 정렬해서 덮어씁니다.
        smSheet.clear();
        smSheet.getRange('A1:C1').setValues([['기호(알파벳)', 'Strain 이름', 'G완료 여부(O/X)']]).setFontWeight('bold').setBackground('#f3f3f3');
        const sortedKeys = sortStrainKeys(Object.keys(newStrainMap));
        const smRows = sortedKeys.map(k => [k, newStrainMap[k].name, newStrainMap[k].g_done ? 'O' : 'X']);
        if (smRows.length > 0) smSheet.getRange(2, 1, smRows.length, 3).setValues(smRows);
      }
    }
  }


  // 시트 다시 그리기
  formatMatingSheet(ss, data);
  formatBreedingSheet(ss, data);
  
  SpreadsheetApp.getUi().alert('✅ 시트 새로고침이 완료되었습니다!');
}


function clearLogsButton() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert('로그 초기화', '정말 모든 로그를 삭제하시겠습니까?', ui.ButtonSet.YES_NO);
  if (response == ui.Button.YES) {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    
    // 1. Log 시트 지우기
    let logSheet = ss.getSheetByName('Log');
    if (logSheet) logSheet.clear();
    
    // 2. DB 시트의 A1에서 logs 배열 비우기
    const dbSheet = ss.getSheetByName('DB');
    if (dbSheet) {
      const rawData = dbSheet.getRange('A1').getValue();
      if (rawData) {
        try {
          const data = JSON.parse(rawData);
          data.logs = [];
          dbSheet.getRange('A1').setValue(JSON.stringify(data));
        } catch(e) {}
      }
    }
    ui.alert('✅ 로그가 성공적으로 초기화되었습니다!\n웹사이트에서 반드시 [동기화] 버튼을 눌러주셔야 브라우저의 로그도 삭제됩니다.');
  }
}


function formatLogSheet(ss, data) {
  let logSheet = ss.getSheetByName('Log');
  if (!logSheet) {
    logSheet = ss.insertSheet('Log');
  }
  logSheet.clear();
  
  if (!data.logs || data.logs.length === 0) {
    logSheet.getRange('A1:D1').setValues([['시간', '분류', '액션', '상세']]);
    return;
  }
  
  const headers = ['시간', '분류', '액션', '상세'];
  const rows = [headers];
  
  data.logs.forEach(log => {
    rows.push([log.ts, log.type, log.action, log.detail]);
  });
  
  logSheet.getRange(1, 1, rows.length, 4).setValues(rows);
  logSheet.getRange(1, 1, 1, 4).setFontWeight('bold').setBackground('#f3f3f3');
  logSheet.autoResizeColumns(1, 4);
}
