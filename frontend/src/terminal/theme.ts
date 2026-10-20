import type { ITheme } from "@xterm/xterm";

export const TERMINAL_FONT = '"JetBrainsMono Nerd Font"';

// Tuned beside the workbench palette; xterm also enforces a minimum contrast ratio.
const dark: ITheme = {
  background: "#0a0c0e",
  foreground: "#dfe3e8",
  cursor: "#ffd343",
  cursorAccent: "#0a0c0e",
  selectionBackground: "#5b9fe055",
  selectionInactiveBackground: "#5b9fe02e",
  scrollbarSliderBackground: "#8b949e2a",
  scrollbarSliderHoverBackground: "#8b949e4d",
  scrollbarSliderActiveBackground: "#8b949e70",
  black: "#4a525c",
  red: "#f0777b",
  green: "#4cc38a",
  yellow: "#ffd343",
  blue: "#5b9fe0",
  magenta: "#c49cf2",
  cyan: "#56c8d8",
  white: "#b9c0c9",
  brightBlack: "#6c7580",
  brightRed: "#f5999c",
  brightGreen: "#6fd6a3",
  brightYellow: "#ffdd6e",
  brightBlue: "#8cc0f2",
  brightMagenta: "#d6b8f7",
  brightCyan: "#7ed8e4",
  brightWhite: "#f3f5f7",
};

const light: ITheme = {
  background: "#fbfbfc",
  foreground: "#1d232b",
  cursor: "#2f73b5",
  cursorAccent: "#fbfbfc",
  selectionBackground: "#2f73b533",
  selectionInactiveBackground: "#2f73b51f",
  scrollbarSliderBackground: "#59636e2a",
  scrollbarSliderHoverBackground: "#59636e4d",
  scrollbarSliderActiveBackground: "#59636e70",
  black: "#24292f",
  red: "#c4303b",
  green: "#17804f",
  yellow: "#8a6400",
  blue: "#2f73b5",
  magenta: "#8250df",
  cyan: "#0e7490",
  white: "#6e7781",
  brightBlack: "#57606a",
  brightRed: "#a40e26",
  brightGreen: "#1a7f37",
  brightYellow: "#6b4d00",
  brightBlue: "#1f5f9c",
  brightMagenta: "#a475f9",
  brightCyan: "#0b6178",
  brightWhite: "#8c959f",
};

export function terminalTheme(theme: string): ITheme {
  return theme === "light" ? light : dark;
}
