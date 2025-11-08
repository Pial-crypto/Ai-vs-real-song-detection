
export const saveToLocal = (key, value) => {
  try {
    const serializedValue = JSON.stringify(value);
    localStorage.setItem(key, serializedValue);
  } catch (error) {
    console.error("Error saving to localStorage:", error);
  }
};


export const getFromLocal = (key) => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch (error) {
    console.error("Error reading from localStorage:", error);
    return null;
  }
};


export const removeFromLocal = (key) => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error("Error removing from localStorage:", error);
  }
};


export const clearLocalStorage = () => {
  try {
    localStorage.clear();
  } catch (error) {
    console.error("Error clearing localStorage:", error);
  }
};
