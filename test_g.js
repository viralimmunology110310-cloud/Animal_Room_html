const fs = require('fs');
const https = require('https');

https.get('https://script.google.com/macros/s/AKfycbzvbbXk5PFzKnhUOGEzorsGl7efvUoxsHXMyPXPZqzAB8paoKr5EZd2MeVPkalNLz-7/exec?action=debugRaw2', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(data));
});
