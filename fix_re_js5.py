with open('apps_script/Re.js', 'r') as f:
    code = f.read()

import re

# We need to insert this logic inside `if (isNewWeek) { ... if (startRow > 3) { ... }`
# Wait, `markerRange` is inside `if (lastRow >= 3)` but scoped to that block. We can just re-fetch or use lastRow.

mating_hide_old = """  if (isNewWeek) {
    startRow = lastRow >= 3 ? lastRow + 1 : 3;
    if (startRow > 3) {
      sheet.hideRows(3, startRow - 3);
    }
  } else {"""

mating_hide_new = """  if (isNewWeek) {
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
  } else {"""

code = code.replace(mating_hide_old, mating_hide_new)

with open('apps_script/Re.js', 'w') as f:
    f.write(code)
print("Re.js updated with hide date logic")
