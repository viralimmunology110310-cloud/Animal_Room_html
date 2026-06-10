const fs = require('fs');
const cages = require('./cages.json');

const cagesArr = Object.values(cages);

cagesArr.forEach(c => {
  if (c.code === 'G' || c.code === 'g') {
    console.log(`Type: ${c.type}, Code: ${c.code}, Gender: ${c.gender}, Count: ${c.bCount}, DOB: ${c.bDob}`);
  }
});
