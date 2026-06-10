import urllib.request
import json

url = "https://script.google.com/macros/s/AKfycbzOL0hNcBt5Dqw_0PjBpGPVE0bJOuRtbtLqCTUSBJUUMEEkbfzqanJGSO9VFjXmaaZ6/exec"
data = {"action":"save","cages":[],"logs":[], "strainMap": {}, "rackRows": 5, "dayMap": {}, "wtRanges": {}}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'text/plain;charset=utf-8'}, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode('utf-8'))
except urllib.error.URLError as e:
    print("Error:", e.read().decode('utf-8') if hasattr(e, 'read') else str(e))

