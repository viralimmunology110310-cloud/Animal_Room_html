const wtRanges = { 'Mon': {min:'', max:''}, 'Tue': {min:'1', max:'10'}, 'Wed': {min:'11', max:'20'} };
function getCageDay(cage, wtRanges) {
  if (cage.code === 'WT') {
    if (cage.type === 'breeding' || cage.type === 'empty') return 'Mon';
    if (wtRanges) {
      const sub = parseInt(cage.subId) || 0;
      if (wtRanges['Mon'] && sub >= parseInt(wtRanges['Mon'].min||9999) && sub <= parseInt(wtRanges['Mon'].max||-1)) return 'Mon';
      if (wtRanges['Tue'] && sub >= parseInt(wtRanges['Tue'].min||9999) && sub <= parseInt(wtRanges['Tue'].max||-1)) return 'Tue';
      if (wtRanges['Wed'] && sub >= parseInt(wtRanges['Wed'].min||9999) && sub <= parseInt(wtRanges['Wed'].max||-1)) return 'Wed';
    }
  }
  return null;
}
console.log("WT breeding:", getCageDay({code:'WT', type:'breeding', subId:'5'}, wtRanges));
console.log("WT mating 5:", getCageDay({code:'WT', type:'mating', subId:'5'}, wtRanges));
console.log("WT mating 15:", getCageDay({code:'WT', type:'mating', subId:'15'}, wtRanges));
