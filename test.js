const cellIdx = 1;
const x = cellIdx % 7;
const cellSize = parseFloat(null) || 92;
const cellGap = 10;
const left = (x * (cellSize + cellGap)) + 'px';
console.log(left);
