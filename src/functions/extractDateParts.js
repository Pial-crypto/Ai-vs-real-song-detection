export function extractDateParts(timestamp) {
  const date = new Date(timestamp);

  return {
    day: date.getUTCDate(),
    month: date.getUTCMonth() + 1, 
    year: date.getUTCFullYear()
  };
}


