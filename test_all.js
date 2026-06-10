const fs = require('fs');
const https = require('https');

https.get('https://script.google.com/macros/s/AKfycbxE8x1MKBbN4iAxPbequLZyDnPN2O6olxAhXt1l5EmgVSNiZn0Zn1Ju5H9sFej-4lBw/exec?action=debugRaw3', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(data));
});
