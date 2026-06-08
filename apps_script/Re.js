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
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`;
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
  if (cage.code === 'G') {
    if (cage.type === 'breeding' || cage.type === 'empty') return 'Mon';
    if (wtRanges) {
      const sub = parseInt(cage.subId) || 0;
      if (wtRanges['Mon'] && sub >= parseInt(wtRanges['Mon'].min||9999) && sub <= parseInt(wtRanges['Mon'].max||-1)) return 'Mon';
      if (wtRanges['Tue'] && sub >= parseInt(wtRanges['Tue'].min||9999) && sub <= parseInt(wtRanges['Tue'].max||-1)) return 'Tue';
      if (wtRanges['Wed'] && sub >= parseInt(wtRanges['Wed'].min||9999) && sub <= parseInt(wtRanges['Wed'].max||-1)) return 'Wed';
    }
  }

  if (dayMap && dayMap[cage.code]) {
    if (typeof dayMap[cage.code] === 'string') {
      return dayMap[cage.code];
    }
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
  return '';
}


function getMondayStr(d) {
  var d2 = new Date(d);
  var day = d2.getDay(),
      diff = d2.getDate() - day + (day == 0 ? -6:1);
  d2.setDate(diff);
  return `${d2.getFullYear()}-${String(d2.getMonth()+1).padStart(2,'0')}-${String(d2.getDate()).padStart(2,'0')}`;
}

function buildMatingNoteRichText(noteStr) {
  if (!noteStr) return SpreadsheetApp.newRichTextValue().setText('').build();
  let builder = SpreadsheetApp.newRichTextValue().setText(noteStr);
  let blackStyle = SpreadsheetApp.newTextStyle().setForegroundColor('#000000').build();
  builder.setTextStyle(0, noteStr.length, blackStyle);
  
  const now = new Date();
  const thresholdDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
  
  const regex = /Baby\s*\d+\s*마리\s*\(\s*(\d{1,2})\s*\/\s*(\d{1,2})\s*\)/g;
  let match;
  while ((match = regex.exec(noteStr)) !== null) {
    const mm = match[1];
    const dd = match[2];
    let yyyy = now.getFullYear();
    let matchDate = new Date(yyyy, parseInt(mm)-1, parseInt(dd));
    if (matchDate > now) {
      matchDate.setFullYear(yyyy - 1);
    }
    
    let color = (matchDate >= thresholdDate) ? '#FF0000' : '#0000FF';
    let textStyle = SpreadsheetApp.newTextStyle().setForegroundColor(color).build();
    builder.setTextStyle(match.index, match.index + match[0].length, textStyle);
  }
  return builder.build();
}

function formatMatingSheet(ss, data) {
  let sheet = ss.getSheetByName('Mating');
  if (!sheet) {
    sheet = ss.insertSheet('Mating');
  }
  sheet.setFrozenRows(2);

  const now = new Date();
  const todayStr = `${now.getFullYear()}.${now.getMonth()+1}.${now.getDate()}`;
  const mondayStr = getMondayStr(now);
  const weekMarker = `WEEK:${mondayStr}`;
  
  sheet.getRange('B1').setValue(todayStr).setFontWeight('bold').setFontSize(12);
  sheet.getRange('C1:J1').merge().setValue('Mating').setHorizontalAlignment('center').setFontWeight('bold').setFontSize(14);
  
  const headers = ['No.', 'C.no.', 'Strain', 'male', 'female', 'D.O.B', 'D.O.M', 'other'];
  sheet.getRange(2, 3, 1, headers.length).setValues([headers]).setFontWeight('bold').setHorizontalAlignment('center').setFontSize(12);

  const lastRow = sheet.getLastRow();
  let startRow = 3;
  let isNewWeek = true;

  if (lastRow >= 3) {
    const markerRange = sheet.getRange(3, 26, lastRow - 2, 1).getValues();
    for (let i = 0; i < markerRange.length; i++) {
      if (markerRange[i][0] === weekMarker) {
        startRow = i + 3;
        isNewWeek = false;
        break;
      }
    }
  }

  if (isNewWeek) {
    startRow = lastRow >= 3 ? lastRow + 1 : 3;
    if (startRow > 3) {
      let markerRange = sheet.getRange(3, 26, lastRow - 2, 1).getValues();
      let prevMarker = markerRange[markerRange.length - 1][0];
      let firstRowOfHiddenBlock = lastRow;
      for (let i = markerRange.length - 1; i >= 0; i--) {
        if (markerRange[i][0] === prevMarker) {
          firstRowOfHiddenBlock = i + 3;
        } else {
          break;
        }
      }
      sheet.getRange(firstRowOfHiddenBlock, 1).setValue(`[${todayStr} 숨김]`).setFontSize(10).setFontWeight('bold').setFontColor('#FF375F');
      sheet.hideRows(3, startRow - 3);
    }
  } else {
    if (lastRow >= startRow) {
      sheet.getRange(startRow, 1, lastRow - startRow + 1, 25).clear();
    }
  }
  sheet.getRange(startRow, 26).setValue(weekMarker);

  const matingCages = data.cages.filter(c => c.type === 'mating');
  matingCages.sort((a, b) => {
    let aCode = a.code || '';
    let bCode = b.code || '';
    if (aCode.length !== bCode.length) return aCode.length - bCode.length;
    if (aCode !== bCode) return aCode.localeCompare(bCode);
    
    let aSub = parseInt(a.subId) || 0;
    let bSub = parseInt(b.subId) || 0;
    if (aSub !== bSub) return aSub - bSub;
    
    let aDob = a.mDob ? new Date(a.mDob).getTime() : Infinity;
    let bDob = b.mDob ? new Date(b.mDob).getTime() : Infinity;
    if (aDob !== bDob) return aDob - bDob;
    
    return (parseInt(a.mMale)||0) - (parseInt(b.mMale)||0);
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
      currentBlock = { start: startRow + idx, num: 1, color: STRAIN_COLORS[colorIdx], code: c.code };
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

    let mNum = c.mMale || '';
    let fNum = c.mFemale || '';
    let rowData = new Array(15).fill('');
    rowData[0] = bCol;
    rowData[1] = globalNo++;
    rowData[2] = c.subId;
    rowData[3] = strainName;
    rowData[4] = mNum;
    rowData[5] = fNum;
    rowData[6] = formatDateDots(c.mDob);
    rowData[7] = formatDateDots(c.mDow);
    rowData[8] = c.notes || '';
    rowData[9] = isGDone ? '' : `${c.code}${c.subId}`;
    rowData[14] = c.id; 
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
    sheet.getRange(startRow, 2, output.length, 15).setValues(output).setHorizontalAlignment('center').setFontSize(12);
    
    let notesRichTexts = output.map(row => [buildMatingNoteRichText(row[8])]);
    sheet.getRange(startRow, 10, output.length, 1).setRichTextValues(notesRichTexts).setHorizontalAlignment('left');
    
    sheet.getRange(startRow, 11, output.length, 1).setFontColors(richTexts.map(c => [c]));
    sheet.getRange(startRow, 2, output.length, 1).setBackgrounds(bColors);
    
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
      if (isGDone) {
        sheet.getRange(b.start, 2, 1, 1).setValue(`${b.code}(G완)`);
      }
      
      let mergedText = `${strainName}
(${b.num})`;
      sheet.getRange(b.start, 5, 1, 1).setValue(mergedText);
      
      sheet.getRange(b.start, 5, b.num, 1).setBackground(b.color).setWrap(true).setVerticalAlignment('middle'); 
      if (b.num > 1) sheet.getRange(b.start, 5, b.num, 1).merge(); 
      sheet.getRange(b.start, 2, b.num, 1).setFontWeight('bold'); 
      sheet.getRange(b.start, 3, b.num, 8).setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    });
    
    sheet.getRange(startRow, 3, output.length, 1).setBorder(true, null, true, null, null, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  }

  const matingWidths = [100, 76, 47, 122, 34, 44, 87, 87, 168, 82];
  matingWidths.forEach((w, i) => sheet.setColumnWidth(2 + i, w));

  sheet.getRange(1, 3, 2, 8).setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  sheet.hideColumns(16); sheet.hideColumns(11); 
}

function formatBreedingSheet(ss, data) {
  let sheet = ss.getSheetByName('Breeding');
  if (!sheet) {
    sheet = ss.insertSheet('Breeding');
  }
  sheet.setFrozenRows(2);

  const now = new Date();
  const todayStr = `${now.getFullYear()}.${now.getMonth()+1}.${now.getDate()}`;
  const mondayStr = getMondayStr(now);
  const weekMarker = `WEEK:${mondayStr}`;
  
  sheet.getRange('B1').setValue(todayStr).setFontWeight('bold').setFontSize(12);
  sheet.getRange('C1:I1').merge().setValue('Breeding').setHorizontalAlignment('center').setFontWeight('bold').setFontSize(14);
  
  const headers = ['No.', 'C.no.', 'Strain', 'sex', 'head', 'D.O.B', 'other'];
  sheet.getRange(2, 3, 1, headers.length).setValues([headers]).setFontWeight('bold').setHorizontalAlignment('center').setFontSize(12);

  const lastRow = sheet.getLastRow();
  let startRow = 3;
  let isNewWeek = true;

  if (lastRow >= 3) {
    const markerRange = sheet.getRange(3, 26, lastRow - 2, 1).getValues();
    for (let i = 0; i < markerRange.length; i++) {
      if (markerRange[i][0] === weekMarker) {
        startRow = i + 3;
        isNewWeek = false;
        break;
      }
    }
  }

  if (isNewWeek) {
    startRow = lastRow >= 3 ? lastRow + 1 : 3;
    if (startRow > 3) {
      let markerRange = sheet.getRange(3, 26, lastRow - 2, 1).getValues();
      let prevMarker = markerRange[markerRange.length - 1][0];
      let firstRowOfHiddenBlock = lastRow;
      for (let i = markerRange.length - 1; i >= 0; i--) {
        if (markerRange[i][0] === prevMarker) {
          firstRowOfHiddenBlock = i + 3;
        } else {
          break;
        }
      }
      sheet.getRange(firstRowOfHiddenBlock, 1).setValue(`[${todayStr} 숨김]`).setFontSize(10).setFontWeight('bold').setFontColor('#FF375F');
      sheet.hideRows(3, startRow - 3);
    }
  } else {
    if (lastRow >= startRow) {
      sheet.getRange(startRow, 1, lastRow - startRow + 1, 25).clear();
    }
  }
  sheet.getRange(startRow, 26).setValue(weekMarker);

  const breedingCages = data.cages.filter(c => c.type === 'breeding' || c.type === 'empty');
  breedingCages.sort((a, b) => {
    let aCode = a.code || '';
    let bCode = b.code || '';
    if (aCode.length !== bCode.length) return aCode.length - bCode.length;
    if (aCode !== bCode) return aCode.localeCompare(bCode);
    
    let aSub = parseInt(a.subId) || 0;
    let bSub = parseInt(b.subId) || 0;
    if (aSub !== bSub) return aSub - bSub;
    
    let aDob = a.bDob ? new Date(a.bDob).getTime() : Infinity;
    let bDob = b.bDob ? new Date(b.bDob).getTime() : Infinity;
    if (aDob !== bDob) return aDob - bDob;
    
    let aGen = (a.gender === 'male') ? 0 : (a.gender === 'female' ? 1 : 2);
    let bGen = (b.gender === 'male') ? 0 : (b.gender === 'female' ? 1 : 2);
    return aGen - bGen;
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
        start: startRow + idx, num: 1, color: STRAIN_COLORS[colorIdx], code: c.code,
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
    rowData[14] = c.id; 
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
    sheet.getRange(startRow, 2, output.length, 15).setValues(output).setHorizontalAlignment('center').setFontSize(12);
    sheet.getRange(startRow, 9, output.length, 1).setFontColors(richTexts.map(c => [c]));
    sheet.getRange(startRow, 10, output.length, 1).setHorizontalAlignment('left');
    sheet.getRange(startRow, 2, output.length, 1).setBackgrounds(bColors);

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
        mergedText = `${strainName}
(${b.totalHeads})`;
        sheet.getRange(b.start, 2, 1, 1).setValue(`${b.code}(G완)`);
      } else {
        mergedText = `${strainName}
(G완: ${b.g_done_heads} / G전: ${b.g_pre})`;
      }
      
      sheet.getRange(b.start, 5, 1, 1).setValue(mergedText);
      sheet.getRange(b.start, 5, b.num, 1).setBackground(b.color).setWrap(true).setVerticalAlignment('middle'); 
      if (b.num > 1) sheet.getRange(b.start, 5, b.num, 1).merge(); 
      
      sheet.getRange(b.start, 2, b.num, 1).setFontWeight('bold'); 
      sheet.getRange(b.start, 3, b.num, 7).setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    });
    
    sheet.getRange(startRow, 3, output.length, 1).setBorder(true, null, true, null, null, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  }

  const breedingWidths = [100, 76, 47, 122, 34, 44, 87, 168, 82];
  breedingWidths.forEach((w, i) => sheet.setColumnWidth(2 + i, w));

  sheet.getRange(1, 3, 2, 7).setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  sheet.hideColumns(16);
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
