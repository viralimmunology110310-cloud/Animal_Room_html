import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://script.google.com/macros/s/AKfycbzSQSRePueoW6OuZ80e0DsnzF9tk2XIKA7YlQbGw4Q85PCYDRuwwrsZ3Fq8DhoX0pZs/exec'
with open('restore_payload.json', 'r') as f:
    data = f.read().encode('utf-8')

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        print(response.getcode())
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code)
    print(e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
