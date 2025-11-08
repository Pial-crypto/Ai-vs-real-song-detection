export function extractDateParts(timestamp) {
  const date = new Date(timestamp);

  return {
    day: date.getUTCDate(),
    month: date.getUTCMonth() + 1, 
    year: date.getUTCFullYear()
  };
}

// Example usage
const timestamp = "2025-11-07T21:52:52.784Z";
const { day, month, year } = extractDateParts(timestamp);

console.log(`Day: ${day}, Month: ${month}, Year: ${year}`);
