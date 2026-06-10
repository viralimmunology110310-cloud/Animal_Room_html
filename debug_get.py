import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

debug_get = """function doGet(e) {
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
       let res = "before doPost";
       try {
         doPost(mockEvent);
         res = "doPost succeeded";
       } catch (err) {
         res = "doPost failed: " + err.toString();
       }
       return ContentService.createTextOutput(res);
    }
  } catch (err) {
    return ContentService.createTextOutput("Sync Failed: " + err.toString());
  }
  return ContentService.createTextOutput("No Data");
}
"""

content = re.sub(r'function doGet\(e\) \{.*?\nfunction doPost\(e\) \{', debug_get + '\nfunction doPost(e) {', content, flags=re.DOTALL)

with open('apps_script/Re.js', 'w') as f:
    f.write(content)
