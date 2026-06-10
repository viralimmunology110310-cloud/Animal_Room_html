import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

new_get = """function doGet(e) {
  const fbUrl = 'https://small-animal-room-default-rtdb.firebaseio.com/dev_animalRoom.json';
  try {
    const response = UrlFetchApp.fetch(fbUrl);
    const data = JSON.parse(response.getContentText());
    if (data) {
       data.action = 'save';
       const mockEvent = {
           postData: {
               contents: JSON.stringify(data)
           }
       };
       doPost(mockEvent);
       return ContentService.createTextOutput("Sync Successful");
    }
  } catch (err) {
    return ContentService.createTextOutput("Sync Failed: " + err.toString());
  }
  return ContentService.createTextOutput("No Data");
}
"""

content = re.sub(r'function doGet\(e\) \{.*?\nfunction doPost\(e\) \{', new_get + '\nfunction doPost(e) {', content, flags=re.DOTALL)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
