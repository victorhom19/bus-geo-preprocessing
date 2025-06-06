import { Point } from "ol/geom";
import { Projection } from "ol/proj";
import { times } from 'lodash-es';

export function capitalizeString(val) {
    return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

const goldenAngle = 137.508;


function selectColor(i) {
  const hue = i * goldenAngle; // use golden angle approximation
  const saturation = 100;
  const brightness = (((i + 50) * goldenAngle) % 30) + 20;

  return `hsl(${hue},${saturation}%,${brightness}%)`;
}

export function palette(count) {
  return times(count, (i) => selectColor(i));
}

export function colorLerp(color1, color2, percent) {
    // Convert the hex colors to RGB values
    const r1 = parseInt(color1.substring(1, 3), 16);
    const g1 = parseInt(color1.substring(3, 5), 16);
    const b1 = parseInt(color1.substring(5, 7), 16);

    const r2 = parseInt(color2.substring(1, 3), 16);
    const g2 = parseInt(color2.substring(3, 5), 16);
    const b2 = parseInt(color2.substring(5, 7), 16);

    // Interpolate the RGB values
    const r = Math.round(r1 + (r2 - r1) * percent);
    const g = Math.round(g1 + (g2 - g1) * percent);
    const b = Math.round(b1 + (b2 - b1) * percent);

    // Convert the interpolated RGB values back to a hex color
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}