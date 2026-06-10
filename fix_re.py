import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

# Fix mDow to dom
content = content.replace("rowData[7] = formatDateDots(c.mDow);", "rowData[7] = formatDateDots(c.dom);")

# Fix doPost DB save chunking
db_save_old = """      // DB 저장 (히든 시트 A1에 JSON 전체 저장)
      let dbSheet = ss.getSheetByName('DB');
      if (!dbSheet) {
        dbSheet = ss.insertSheet('DB');
        dbSheet.hideSheet();
      }
      dbSheet.getRange('A1').setValue(rawData);"""
db_save_new = """      // DB 저장 (히든 시트 청크 단위 분할 저장)
      let dbSheet = ss.getSheetByName('DB');
      if (!dbSheet) {
        dbSheet = ss.insertSheet('DB');
        dbSheet.hideSheet();
      }
      dbSheet.clear();
      const CHUNK_SIZE = 40000;
      const chunks = [];
      for (let i = 0; i < rawData.length; i += CHUNK_SIZE) {
        chunks.push([rawData.substring(i, i + CHUNK_SIZE)]);
      }
      if (chunks.length > 0) {
        dbSheet.getRange(1, 1, chunks.length, 1).setValues(chunks);
      }"""
content = content.replace(db_save_old, db_save_new)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
