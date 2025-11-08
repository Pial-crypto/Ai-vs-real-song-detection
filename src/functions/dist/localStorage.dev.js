"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.clearLocalStorage = exports.removeFromLocal = exports.getFromLocal = exports.saveToLocal = void 0;

var saveToLocal = function saveToLocal(key, value) {
  try {
    var serializedValue = JSON.stringify(value);
    localStorage.setItem(key, serializedValue);
  } catch (error) {
    console.error("Error saving to localStorage:", error);
  }
};

exports.saveToLocal = saveToLocal;

var getFromLocal = function getFromLocal(key) {
  try {
    var item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch (error) {
    console.error("Error reading from localStorage:", error);
    return null;
  }
};

exports.getFromLocal = getFromLocal;

var removeFromLocal = function removeFromLocal(key) {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error("Error removing from localStorage:", error);
  }
};

exports.removeFromLocal = removeFromLocal;

var clearLocalStorage = function clearLocalStorage() {
  try {
    localStorage.clear();
  } catch (error) {
    console.error("Error clearing localStorage:", error);
  }
};

exports.clearLocalStorage = clearLocalStorage;