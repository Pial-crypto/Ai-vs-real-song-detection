"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.extractDateParts = extractDateParts;

function extractDateParts(timestamp) {
  var date = new Date(timestamp);
  return {
    day: date.getUTCDate(),
    month: date.getUTCMonth() + 1,
    year: date.getUTCFullYear()
  };
}