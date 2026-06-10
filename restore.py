import json

with open('backup.json', 'r') as f:
    data = json.load(f)

if isinstance(data.get('cages'), dict):
    data['cages'] = list(data['cages'].values())

if isinstance(data.get('logs'), dict):
    data['logs'] = list(data['logs'].values())

payload = {
    'key': 'my-secret-password-1234',
    'action': 'save'
}
payload.update(data)

with open('restore_payload.json', 'w') as f:
    json.dump(payload, f)
