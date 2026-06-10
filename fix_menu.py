import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

menu_code = """function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🐭 Animal Room')
      .addItem('🔄 시트 새로고침 (매칭표 적용)', 'syncFromSheetButton')
      .addItem('⚠️ 백그라운드 동기화 권한 허용', 'authorizeWebhook')
      .addToUi();
}

function authorizeWebhook() {
  try {
    UrlFetchApp.fetch('https://google.com');
    SpreadsheetApp.getUi().alert('✅ 백그라운드 동기화 권한 허용이 완료되었습니다!\\n이제 기자재예약 시트에서 글을 쓰면 자동으로 연동됩니다.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('권한이 이미 허용되었거나 오류가 발생했습니다.');
  }
}
"""

content = re.sub(r'function onOpen\(\) \{.*?\n\}\n', menu_code, content, flags=re.DOTALL)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
