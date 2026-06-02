const admin = require("firebase-admin");

let localCages = [];
let localCagesObj = {};
localCages.forEach(c => localCagesObj[c.id] = c);

let firebaseDataCages = [ { id: "c_1", code: "A" } ];
firebaseDataCages["c_2"] = { id: "c_2", code: "B" }; // mixed array from Firebase update

let rawCages = firebaseDataCages || {};
let cages = Array.isArray(rawCages) ? rawCages.filter(c => c) : Object.values(rawCages).filter(c => c);

console.log("Cages:", cages);
