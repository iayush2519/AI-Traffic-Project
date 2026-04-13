// Map text labels to HEX colors
export const congestionColors = {
  low: '#00e676',      // Green
  medium: '#ffeb3b',   // Yellow
  high: '#ff9100',     // Orange
  severe: '#ff1744'    // Red
};

export const getCongestionColor = (label) => {
  return congestionColors[label] || congestionColors.low;
};

// Map score [0, 1] to a color gradient if needed
export const getScoreColor = (score) => {
  if (score < 0.25) return congestionColors.low;
  if (score < 0.50) return congestionColors.medium;
  if (score < 0.75) return congestionColors.high;
  return congestionColors.severe;
};
