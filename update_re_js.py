import re

with open('apps_script/Re.js', 'r') as f:
    code = f.read()

# 1. Update formatDateDots
code = re.sub(
    r"function formatDateDots\(dateStr\) \{.*?\n\}",
    r"""function formatDateDots(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`;
}""",
    code,
    flags=re.DOTALL
)

# 2. Add getMondayStr and buildMatingNoteRichText
helper_funcs = """
function getMondayStr(d) {
  var d2 = new Date(d);
  var day = d2.getDay(),
      diff = d2.getDate() - day + (day == 0 ? -6:1);
  d2.setDate(diff);
  return `${d2.getFullYear()}-${String(d2.getMonth()+1).padStart(2,'0')}-${String(d2.getDate()).padStart(2,'0')}`;
}

function buildMatingNoteRichText(noteStr, mondayStr) {
  if (!noteStr) return SpreadsheetApp.newRichTextValue().setText('').build();
  let builder = SpreadsheetApp.newRichTextValue().setText(noteStr);
  
  const regex = /Baby \d+마리\((\d{1,2})\/(\d{1,2})\)/g;
  let match;
  while ((match = regex.exec(noteStr)) !== null) {
    const mm = match[1];
    const dd = match[2];
    const dateObj = new Date(new Date().getFullYear(), parseInt(mm)-1, parseInt(dd));
    const dateStr = `${dateObj.getFullYear()}-${String(dateObj.getMonth()+1).padStart(2,'0')}-${String(dateObj.getDate()).padStart(2,'0')}`;
    let color = '#0000FF'; // Blue
    if (dateStr >= mondayStr) {
      color = '#FF0000'; // Red
    }
    let textStyle = SpreadsheetApp.newTextStyle().setForegroundColor(color).build();
    builder.setTextStyle(match.index, match.index + match[0].length, textStyle);
  }
  return builder.build();
}
"""

if "function getMondayStr" not in code:
    code = code.replace("function formatMatingSheet", helper_funcs + "\nfunction formatMatingSheet")

# 3. Modify formatMatingSheet
mating_sheet_func = """function formatMatingSheet(ss, data) {
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
  
  const headers = ['No.', 'C.no.', 'Strain', 'male', 'female', 'D.O.B', 'D.O.W', 'other'];
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
    rowData[2] = strainCNo;
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
    
    let notesRichTexts = output.map(row => [buildMatingNoteRichText(row[8], mondayStr)]);
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
      sheet.getRange(b.start, 5, b.num, 1).setBackground(b.color); 
      if (b.num > 1) sheet.getRange(b.start, 5, b.num, 1).merge().setVerticalAlignment('middle'); 
      sheet.getRange(b.start, 2, b.num, 1).setFontWeight('bold'); 
      sheet.getRange(b.start, 3, b.num, 8).setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    });
    
    sheet.getRange(startRow, 3, output.length, 1).setBorder(true, null, true, null, null, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  }

  const matingWidths = [100, 76, 47, 122, 34, 44, 87, 87, 168, 82];
  matingWidths.forEach((w, i) => sheet.setColumnWidth(2 + i, w));

  sheet.getRange(1, 3, 2, 8).setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  sheet.hideColumns(16); sheet.hideColumns(11); 
}"""

code = re.sub(r"function formatMatingSheet\(ss, data\) \{.*?\nfunction formatBreedingSheet", mating_sheet_func + "\n\nfunction formatBreedingSheet", code, flags=re.DOTALL)

# 4. Modify formatBreedingSheet
breeding_sheet_func = """function formatBreedingSheet(ss, data) {
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
        mergedText = `${strainName}\\n(${b.totalHeads})`;
        sheet.getRange(b.start, 2, 1, 1).setValue(`${b.code}(G완)`);
      } else {
        mergedText = `${strainName}\\n(G완: ${b.g_done_heads} / G전: ${b.g_pre})`;
      }
      
      sheet.getRange(b.start, 5, 1, 1).setValue(mergedText);
      sheet.getRange(b.start, 5, b.num, 1).setBackground(b.color); 
      if (b.num > 1) sheet.getRange(b.start, 5, b.num, 1).merge().setVerticalAlignment('middle'); 
      
      sheet.getRange(b.start, 2, b.num, 1).setFontWeight('bold'); 
      sheet.getRange(b.start, 3, b.num, 7).setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    });
    
    sheet.getRange(startRow, 3, output.length, 1).setBorder(true, null, true, null, null, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  }

  const breedingWidths = [100, 76, 47, 122, 34, 44, 87, 168, 82];
  breedingWidths.forEach((w, i) => sheet.setColumnWidth(2 + i, w));

  sheet.getRange(1, 3, 2, 7).setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  sheet.hideColumns(16);
}"""

code = re.sub(r"function formatBreedingSheet\(ss, data\) \{.*?\n// ── 구글 시트 전용 메뉴 추가 ──", breeding_sheet_func + "\n\n// ── 구글 시트 전용 메뉴 추가 ──", code, flags=re.DOTALL)

with open('apps_script/Re.js', 'w') as f:
    f.write(code)

print("Updated Re.js")
