import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  BookOpen,
  CircleAlert,
  CircleCheck,
  Compass,
  CornerDownLeft,
  House,
  Info,
  Keyboard,
  ListChecks,
  ListTree,
  Moon,
  Repeat2,
  Search,
  Settings as SettingsIcon,
  Sun,
  X,
} from "lucide-react";
import { api, ApiError } from "./api";
import {
  AppContext,
  isMod,
  mod,
  useApp,
  type App as AppValue,
  type ConfirmOptions,
  type ToastKind,
} from "./context";
import { Dialog, Kbd, Logo, Spinner, StatusIcon } from "./components/ui";
import { Game } from "./pages/Game";
import { Home } from "./pages/Home";
import { ReviewSession, Reviews } from "./pages/Reviews";
import { Settings, Topics } from "./pages/Settings";
import { Syllabus } from "./pages/Syllabus";
import { Welcome } from "./pages/Welcome";
import { learnPath, navigate, parse, usePath } from "./router";
import type { AppState, Catalog } from "./types";
import { Workbench } from "./workbench/Workbench";

type Toast = { id: number; text: string; kind: ToastKind };
type Pending = ConfirmOptions & { resolve: (value: boolean) => void };

function systemTheme(): "light" | "dark" {
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

export function App() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [state, setState] = useState<AppState | null>(null);
  const [problem, setProblem] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [pending, setPending] = useState<Pending | null>(null);
  const [palette, setPalette] = useState(false);
  const [shortcuts, setShortcuts] = useState(false);
  const [topbar, setTopbar] = useState<HTMLElement | null>(null);
  const [system, setSystem] = useState(systemTheme);
  const path = usePath();
  const route = parse(path);

  useEffect(() => {
    const token = new URLSearchParams(location.hash.slice(1)).get("token");
    const signIn = token
      ? api("/session", { token }).catch(() => undefined)
      : Promise.resolve(undefined);
    if (token) history.replaceState(null, "", location.pathname);
    signIn
      .then(() => Promise.all([api<Catalog>("/catalog"), api<AppState>("/state")]))
      .then(([loadedCatalog, loadedState]) => {
        setCatalog(loadedCatalog);
        setState(loadedState);
      })
      .catch((error: ApiError) => setProblem(error.message));
  }, []);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: light)");
    const change = () => setSystem(systemTheme());
    media.addEventListener("change", change);
    return () => media.removeEventListener("change", change);
  }, []);

  // Progress changes inside pages, so every navigation shows fresh statuses.
  const signedIn = catalog !== null;
  useEffect(() => {
    if (signedIn)
      api<AppState>("/state")
        .then(setState)
        .catch(() => undefined);
  }, [path, signedIn]);

  const preference = state?.settings.theme ?? "dark";
  const theme = preference === "system" ? system : preference;
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const toast = useCallback((text: string, kind: ToastKind = "info") => {
    const id = Date.now() + Math.random();
    setToasts((all) => [...all.slice(-3), { id, text, kind }]);
    window.setTimeout(
      () => setToasts((all) => all.filter((item) => item.id !== id)),
      kind === "error" ? 9000 : 5000,
    );
  }, []);
  const fail = useCallback(
    (error: unknown) => toast(error instanceof Error ? error.message : String(error), "error"),
    [toast],
  );
  const refresh = useCallback(async () => {
    try {
      setState(await api<AppState>("/state"));
    } catch (error) {
      fail(error);
    }
  }, [fail]);
  const confirm = useCallback(
    (options: ConfirmOptions) =>
      new Promise<boolean>((resolve) => setPending({ ...options, resolve })),
    [],
  );
  const setTheme = useCallback(
    (value: "dark" | "light" | "system") => {
      setState((current) => (current ? { ...current, settings: { theme: value } } : current));
      api<AppState>("/settings", { theme: value }).then(setState).catch(fail);
    },
    [fail],
  );

  useEffect(() => {
    const key = (event: KeyboardEvent) => {
      if (event.defaultPrevented) return;
      if (isMod(event) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setPalette((open) => !open);
        return;
      }
      const target = event.target as HTMLElement;
      const typing =
        target.closest("input, textarea, .cm-editor, .xterm, [contenteditable]") !== null;
      if (!typing && event.key === "?" && !event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        setShortcuts(true);
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, []);

  const value = useMemo<AppValue | null>(
    () =>
      catalog && state
        ? {
            catalog,
            state,
            setState,
            refresh,
            toast,
            fail,
            confirm,
            theme,
            setTheme,
            openPalette: () => setPalette(true),
            openShortcuts: () => setShortcuts(true),
            topbar,
          }
        : null,
    [catalog, state, refresh, toast, fail, confirm, theme, setTheme, topbar],
  );

  if (problem) return <Disconnected message={problem} />;
  if (!value || !state) {
    return (
      <div className="boot">
        <Logo size={48} />
        <Spinner size={18} />
      </div>
    );
  }

  let page: ReactNode;
  if (!state.onboarded && route.page !== "settings") page = <Welcome />;
  else if (route.page === "learn") page = <Workbench key={route.id} id={route.id} />;
  else if (route.page === "syllabus") page = <Syllabus />;
  else if (route.page === "game") page = <Game />;
  else if (route.page === "review") page = <Reviews />;
  else if (route.page === "review-session")
    page = <ReviewSession key={route.chapter} chapter={route.chapter} />;
  else if (route.page === "topics") page = <Topics />;
  else if (route.page === "settings") page = <Settings />;
  else page = <Home />;

  const welcome = !state.onboarded && route.page !== "settings";
  return (
    <AppContext.Provider value={value}>
      <div className={`app ${welcome ? "bare" : ""} ${route.page === "learn" ? "learning" : ""}`}>
        {!welcome && <Rail route={route.page} />}
        <main className="main">
          {!welcome && (
            <header className="topbar">
              <div className="topbar-slot" ref={setTopbar} />
              <button className="search-button" onClick={() => setPalette(true)}>
                <Search size={14} />
                <span>Search lessons</span>
                <Kbd>{mod}K</Kbd>
              </button>
            </header>
          )}
          <div className="content">{page}</div>
        </main>
      </div>
      {palette && <Palette onClose={() => setPalette(false)} />}
      {shortcuts && <Shortcuts onClose={() => setShortcuts(false)} />}
      {pending && (
        <Dialog
          title={pending.title}
          onClose={() => {
            pending.resolve(false);
            setPending(null);
          }}
          footer={
            <>
              <button
                className="btn"
                onClick={() => {
                  pending.resolve(false);
                  setPending(null);
                }}
              >
                Cancel
              </button>
              <button
                className={`btn ${pending.danger ? "danger" : "primary"}`}
                data-autofocus
                onClick={() => {
                  pending.resolve(true);
                  setPending(null);
                }}
              >
                {pending.confirm}
              </button>
            </>
          }
        >
          <p>{pending.body}</p>
        </Dialog>
      )}
      <div className="toasts" role="status" aria-live="polite">
        {toasts.map((item) => (
          <div key={item.id} className={`toast ${item.kind}`}>
            {item.kind === "error" ? (
              <CircleAlert size={16} />
            ) : item.kind === "success" ? (
              <CircleCheck size={16} />
            ) : (
              <Info size={16} />
            )}
            <span>{item.text}</span>
            <button
              className="icon-btn"
              aria-label="Dismiss"
              onClick={() =>
                setToasts((all) => all.filter((toastItem) => toastItem.id !== item.id))
              }
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </AppContext.Provider>
  );
}

function Rail({ route }: { route: string }) {
  const app = useApp();
  const { state, theme, setTheme } = app;
  const resume = state.last_lesson ?? state.next?.id;
  const items: [string, string, typeof House, string][] = [
    ["home", "Home", House, "/"],
    ["syllabus", "Syllabus", ListTree, "/syllabus"],
    ["learn", "Current lesson", BookOpen, resume ? learnPath(resume) : "/"],
    ["game", "Your game", Compass, "/game"],
    ["review", "Review", Repeat2, "/review"],
    ["topics", "Known topics", ListChecks, "/topics"],
  ];
  return (
    <nav className="rail" aria-label="Main">
      <a
        href="/"
        className="rail-logo"
        aria-label="Pytuitor home"
        onClick={(event) => {
          event.preventDefault();
          navigate("/");
        }}
      >
        <Logo size={30} />
      </a>
      {items.map(([page, label, Icon, href]) => {
        const on = route === page || (page === "review" && route === "review-session");
        return (
          <a
            key={page}
            href={href}
            className={`rail-item ${on ? "on" : ""}`}
            aria-current={on ? "page" : undefined}
            data-tip={label}
            aria-label={label}
            onClick={(event) => {
              event.preventDefault();
              navigate(href);
            }}
          >
            <Icon size={19} strokeWidth={1.8} />
            {page === "review" && state.review_suggested && <span className="rail-dot" />}
          </a>
        );
      })}
      <span className="rail-spacer" />
      <button
        className="rail-item"
        data-tip="Keyboard shortcuts"
        aria-label="Keyboard shortcuts"
        onClick={app.openShortcuts}
      >
        <Keyboard size={19} strokeWidth={1.8} />
      </button>
      <button
        className="rail-item"
        data-tip={theme === "dark" ? "Light theme" : "Dark theme"}
        aria-label={theme === "dark" ? "Switch to the light theme" : "Switch to the dark theme"}
        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      >
        {theme === "dark" ? (
          <Sun size={19} strokeWidth={1.8} />
        ) : (
          <Moon size={19} strokeWidth={1.8} />
        )}
      </button>
      <a
        href="/settings"
        className={`rail-item ${route === "settings" ? "on" : ""}`}
        data-tip="Settings"
        aria-label="Settings"
        onClick={(event) => {
          event.preventDefault();
          navigate("/settings");
        }}
      >
        <SettingsIcon size={19} strokeWidth={1.8} />
      </a>
    </nav>
  );
}

type Entry = {
  id: string;
  title: string;
  detail: string;
  group: string;
  icon: ReactNode;
  run: () => void;
};

function Palette({ onClose }: { onClose: () => void }) {
  const { catalog, state, setTheme, theme } = useApp();
  const [query, setQuery] = useState("");
  const [index, setIndex] = useState(0);
  const list = useRef<HTMLUListElement>(null);
  const entries = useMemo<Entry[]>(() => {
    const go = (path: string) => () => navigate(path);
    const pages: Entry[] = [
      {
        id: "p-home",
        title: "Home",
        detail: "Continue and browse chapters",
        group: "Go to",
        icon: <House size={15} />,
        run: go("/"),
      },
      {
        id: "p-syllabus",
        title: "Syllabus",
        detail: "Every chapter and lesson",
        group: "Go to",
        icon: <ListTree size={15} />,
        run: go("/syllabus"),
      },
      {
        id: "p-game",
        title: "Your game",
        detail: "Lantern Reach milestones and versions",
        group: "Go to",
        icon: <Compass size={15} />,
        run: go("/game"),
      },
      {
        id: "p-review",
        title: "Review",
        detail: "Optional mixed practice",
        group: "Go to",
        icon: <Repeat2 size={15} />,
        run: go("/review"),
      },
      {
        id: "p-topics",
        title: "Known topics",
        detail: "Choose what Continue skips",
        group: "Go to",
        icon: <ListChecks size={15} />,
        run: go("/topics"),
      },
      {
        id: "p-settings",
        title: "Settings",
        detail: "Theme, profile, start over",
        group: "Go to",
        icon: <SettingsIcon size={15} />,
        run: go("/settings"),
      },
      {
        id: "a-theme",
        title: theme === "dark" ? "Switch to light theme" : "Switch to dark theme",
        detail: "Appearance",
        group: "Actions",
        icon: theme === "dark" ? <Sun size={15} /> : <Moon size={15} />,
        run: () => setTheme(theme === "dark" ? "light" : "dark"),
      },
    ];
    const lessons: Entry[] = catalog.chapters.flatMap((chapter) =>
      chapter.activities.map((id) => {
        const item = catalog.activities[id];
        return {
          id,
          title: item.title,
          detail: `Ch ${chapter.number} · ${chapter.title} · ${item.concepts.slice(0, 3).join(", ")}`,
          group: item.milestone ? "Game milestones" : "Lessons",
          icon: <StatusIcon status={state.statuses[id]} size={15} />,
          run: go(learnPath(id)),
        };
      }),
    );
    return [...pages, ...lessons];
  }, [catalog, state.statuses, setTheme, theme]);

  const needle = query.trim().toLowerCase();
  const results = useMemo(() => {
    if (!needle)
      return entries
        .slice(0, 7)
        .concat(state.next ? entries.filter((e) => e.id === state.next!.id) : []);
    const words = needle.split(/\s+/);
    return entries
      .map((entry) => {
        const haystack = `${entry.title} ${entry.detail} ${
          catalog.activities[entry.id]?.concepts.join(" ") ?? ""
        } ${catalog.activities[entry.id]?.subtitle ?? ""}`.toLowerCase();
        if (!words.every((word) => haystack.includes(word))) return null;
        const score = entry.title.toLowerCase().startsWith(needle)
          ? 0
          : entry.title.toLowerCase().includes(needle)
            ? 1
            : 2;
        return { entry, score };
      })
      .filter((item): item is { entry: Entry; score: number } => item !== null)
      .sort((a, b) => a.score - b.score)
      .slice(0, 40)
      .map((item) => item.entry);
  }, [entries, needle, catalog, state.next]);

  useEffect(() => {
    list.current?.querySelector(".on")?.scrollIntoView({ block: "nearest" });
  }, [index]);

  const choose = (entry: Entry | undefined) => {
    if (!entry) return;
    onClose();
    entry.run();
  };

  return (
    <div
      className="scrim palette-scrim"
      onMouseDown={(event) => event.target === event.currentTarget && onClose()}
    >
      <div className="palette" role="dialog" aria-label="Search">
        <label className="palette-input">
          <Search size={17} />
          <input
            autoFocus
            value={query}
            placeholder="Search lessons, topics, and pages"
            aria-label="Search"
            role="combobox"
            aria-expanded="true"
            aria-controls="palette-results"
            onChange={(event) => {
              setQuery(event.target.value);
              setIndex(0);
            }}
            onKeyDown={(event) => {
              if (event.key === "ArrowDown") {
                event.preventDefault();
                setIndex((value) => Math.min(results.length - 1, value + 1));
              } else if (event.key === "ArrowUp") {
                event.preventDefault();
                setIndex((value) => Math.max(0, value - 1));
              } else if (event.key === "Enter") {
                event.preventDefault();
                choose(results[index]);
              } else if (event.key === "Escape") onClose();
            }}
          />
          <Kbd>Esc</Kbd>
        </label>
        <ul className="palette-results" id="palette-results" role="listbox" ref={list}>
          {results.map((entry, position) => {
            const header =
              position === 0 || results[position - 1].group !== entry.group ? entry.group : null;
            return (
              <li key={entry.id} role="presentation">
                {header && <p className="palette-group">{header}</p>}
                <button
                  role="option"
                  aria-selected={position === index}
                  className={position === index ? "on" : ""}
                  onMouseMove={() => setIndex(position)}
                  onClick={() => choose(entry)}
                >
                  <span className="palette-icon">{entry.icon}</span>
                  <span className="palette-text">
                    <strong>{entry.title}</strong>
                    <span>{entry.detail}</span>
                  </span>
                  {position === index && <CornerDownLeft size={14} className="muted" />}
                </button>
              </li>
            );
          })}
          {!results.length && <li className="palette-empty">No lessons match "{query}".</li>}
        </ul>
      </div>
    </div>
  );
}

function Shortcuts({ onClose }: { onClose: () => void }) {
  const rows: [string, ReactNode][] = [
    ["Search lessons and pages", <Kbd key="k">{mod} K</Kbd>],
    ["Run your program in the terminal", <Kbd key="r">{mod} ↵</Kbd>],
    ["Check your work", <Kbd key="c">{mod} ⇧ ↵</Kbd>],
    ["Save now (saving is automatic)", <Kbd key="s">{mod} S</Kbd>],
    ["Focus the terminal", <Kbd key="t">Ctrl `</Kbd>],
    ["Find in the editor", <Kbd key="f">{mod} F</Kbd>],
    ["Find in the terminal", <Kbd key="ft">{mod === "⌘" ? "⌘ F" : "Ctrl ⇧ F"}</Kbd>],
    ["Stop a running program", <Kbd key="x">Ctrl C</Kbd>],
    ["End typed input (EOF)", <Kbd key="d">Ctrl D</Kbd>],
    ["Indent or outdent a selection", <Kbd key="i">Tab / ⇧ Tab</Kbd>],
    ["Show these shortcuts", <Kbd key="q">?</Kbd>],
  ];
  return (
    <Dialog title="Keyboard shortcuts" onClose={onClose}>
      <dl className="shortcut-list">
        {rows.map(([label, keys]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{keys}</dd>
          </div>
        ))}
      </dl>
    </Dialog>
  );
}

function Disconnected({ message }: { message: string }) {
  return (
    <div className="disconnected">
      <Logo size={52} />
      <h1>Open Pytuitor from its launcher</h1>
      <p>{message}</p>
      <p className="muted">
        Run <code className="inline">pytuitor-web</code> in a terminal. It opens this page with a
        one-time sign-in link.
      </p>
    </div>
  );
}
