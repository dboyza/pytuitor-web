import { useSyncExternalStore } from "react";

export type Route =
  | { page: "home" }
  | { page: "syllabus" }
  | { page: "learn"; id: string }
  | { page: "game" }
  | { page: "review" }
  | { page: "review-session"; chapter: string }
  | { page: "topics" }
  | { page: "settings" };

export function parse(path: string): Route {
  const parts = path.split("/").filter(Boolean).map(decodeURIComponent);
  switch (parts[0]) {
    case "syllabus":
      return { page: "syllabus" };
    case "learn":
      return parts[1] ? { page: "learn", id: parts[1] } : { page: "home" };
    case "game":
      return { page: "game" };
    case "review":
      return parts[1] ? { page: "review-session", chapter: parts[1] } : { page: "review" };
    case "topics":
      return { page: "topics" };
    case "settings":
      return { page: "settings" };
    default:
      return { page: "home" };
  }
}

const listeners = new Set<() => void>();
window.addEventListener("popstate", () => listeners.forEach((fn) => fn()));

export function navigate(path: string, replace = false) {
  if (path === location.pathname) return;
  if (replace) history.replaceState(null, "", path);
  else history.pushState(null, "", path);
  listeners.forEach((fn) => fn());
  window.scrollTo(0, 0);
}

function subscribe(fn: () => void) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function usePath() {
  return useSyncExternalStore(subscribe, () => location.pathname);
}

export function learnPath(id: string) {
  return `/learn/${encodeURIComponent(id)}`;
}
