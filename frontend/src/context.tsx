import { createContext, useContext } from "react";
import type { AppState, Catalog } from "./types";

export type ToastKind = "info" | "success" | "error";
export type ConfirmOptions = {
  title: string;
  body: string;
  confirm: string;
  danger?: boolean;
};

export type App = {
  catalog: Catalog;
  state: AppState;
  setState: (state: AppState) => void;
  refresh: () => Promise<void>;
  toast: (text: string, kind?: ToastKind) => void;
  fail: (error: unknown) => void;
  confirm: (options: ConfirmOptions) => Promise<boolean>;
  theme: "dark" | "light";
  setTheme: (theme: "dark" | "light" | "system") => void;
  openPalette: () => void;
  openShortcuts: () => void;
  topbar: HTMLElement | null;
};

export const AppContext = createContext<App | null>(null);

export function useApp(): App {
  const value = useContext(AppContext);
  if (!value) throw new Error("useApp needs the App provider");
  return value;
}

export const mac = /Mac|iPhone|iPad/.test(navigator.platform);
export const mod = mac ? "⌘" : "Ctrl";

export function isMod(event: KeyboardEvent | React.KeyboardEvent) {
  return mac ? event.metaKey : event.ctrlKey;
}
