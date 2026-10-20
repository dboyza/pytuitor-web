import { useEffect, useImperativeHandle, useRef, useState, type Ref } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { SearchAddon } from "@xterm/addon-search";
import { Unicode11Addon } from "@xterm/addon-unicode11";
import { WebLinksAddon } from "@xterm/addon-web-links";
import { WebglAddon } from "@xterm/addon-webgl";
import "@xterm/xterm/css/xterm.css";
import { ArrowDown, ArrowUp, LoaderCircle, Plus, X } from "lucide-react";
import type { ConsoleSession } from "../types";
import { mac } from "../context";
import { TERMINAL_FONT, terminalTheme } from "./theme";

export type ConsoleHandle = {
  focus: () => void;
  clear: () => void;
  find: () => void;
};
type Link = "connecting" | "live" | "reconnecting" | "ended" | "lost";

// Close codes sent by the server, matching pytuitor_web/web.py.
const ENDED = 4001;
const LAGGING = 4002;
const UNKNOWN = 4004;
const REFUSED = 1008;
const encoder = new TextEncoder();

export function ConsoleView({
  session,
  active,
  theme,
  fontSize,
  onTitle,
  onEnded,
  onRestart,
  onClose,
  endedText,
  ref,
}: {
  session: ConsoleSession;
  active: boolean;
  theme: string;
  fontSize: number;
  onTitle?: (title: string) => void;
  onEnded?: () => void;
  onRestart?: () => void;
  onClose?: () => void;
  endedText?: string;
  ref?: Ref<ConsoleHandle>;
}) {
  const host = useRef<HTMLDivElement>(null);
  const terminal = useRef<Terminal | null>(null);
  const fit = useRef<FitAddon | null>(null);
  const search = useRef<SearchAddon | null>(null);
  const [link, setLink] = useState<Link>("connecting");
  const [finding, setFinding] = useState(false);
  const [query, setQuery] = useState("");
  const findInput = useRef<HTMLInputElement>(null);
  const callbacks = useRef({ onTitle, onEnded });
  const settings = useRef({ theme, fontSize });
  useEffect(() => {
    callbacks.current = { onTitle, onEnded };
    settings.current = { theme, fontSize };
  });

  useImperativeHandle(ref, () => ({
    focus: () => terminal.current?.focus(),
    clear: () => terminal.current?.clear(),
    find: () => {
      setFinding(true);
      requestAnimationFrame(() => findInput.current?.select());
    },
  }));

  useEffect(() => {
    let disposed = false;
    let socket: WebSocket | null = null;
    let timer = 0;
    let retries = 0;
    const term = new Terminal({
      allowProposedApi: true,
      cursorBlink: true,
      cursorStyle: "bar",
      cursorInactiveStyle: "outline",
      fontFamily: `${TERMINAL_FONT}, ui-monospace, Menlo, monospace`,
      fontSize: settings.current.fontSize,
      lineHeight: 1.3,
      minimumContrastRatio: 4.5,
      macOptionClickForcesSelection: true,
      rightClickSelectsWord: true,
      scrollback: 10000,
      theme: terminalTheme(settings.current.theme),
    });
    const fitter = new FitAddon();
    const finder = new SearchAddon();
    term.loadAddon(fitter);
    term.loadAddon(finder);
    term.loadAddon(new Unicode11Addon());
    term.unicode.activeVersion = "11";
    term.loadAddon(new WebLinksAddon((_, uri) => window.open(uri, "_blank", "noopener")));
    terminal.current = term;
    fit.current = fitter;
    search.current = finder;

    const send = (data: string | Uint8Array<ArrayBuffer>) => {
      if (socket?.readyState === WebSocket.OPEN) socket.send(data);
    };
    const sendSize = () => send(JSON.stringify({ cols: term.cols, rows: term.rows }));
    term.onData((data) => send(encoder.encode(data)));
    term.onBinary((data) => send(Uint8Array.from(data, (char) => char.charCodeAt(0))));
    term.onResize(sendSize);
    term.onTitleChange((title) => callbacks.current.onTitle?.(title));
    term.attachCustomKeyEventHandler((event) => {
      if (event.type !== "keydown") return true;
      const key = event.key.toLowerCase();
      const command = mac ? event.metaKey : event.ctrlKey && event.shiftKey;
      // Workbench shortcuts pass through to the window instead of the shell.
      if ((mac ? event.metaKey : event.ctrlKey) && (key === "enter" || key === "k")) return false;
      if (event.ctrlKey && key === "`") return false;
      if (command && key === "f") {
        event.preventDefault();
        setFinding(true);
        requestAnimationFrame(() => findInput.current?.select());
        return false;
      }
      // Linux and Windows terminals copy and paste with Ctrl+Shift, leaving Ctrl+C for the shell.
      if (!mac && event.ctrlKey && event.shiftKey && key === "c") {
        if (term.hasSelection()) void navigator.clipboard.writeText(term.getSelection());
        return false;
      }
      return !(!mac && event.ctrlKey && event.shiftKey && key === "v");
    });

    const connect = () => {
      const scheme = location.protocol === "https:" ? "wss" : "ws";
      socket = new WebSocket(`${scheme}://${location.host}/api/consoles/${session.id}/stream`);
      socket.binaryType = "arraybuffer";
      let replaying = true;
      socket.onopen = () => {
        retries = 0;
        setLink("live");
        sendSize();
      };
      socket.onmessage = (event) => {
        // Each connection starts with the full scrollback, so redraw from a clean screen.
        if (replaying) term.reset();
        replaying = false;
        term.write(new Uint8Array(event.data as ArrayBuffer));
      };
      socket.onclose = (event) => {
        if (disposed) return;
        if (event.code === ENDED) {
          setLink("ended");
          callbacks.current.onEnded?.();
        } else if (event.code === UNKNOWN || event.code === REFUSED) setLink("lost");
        else {
          setLink("reconnecting");
          const delay = event.code === LAGGING ? 0 : Math.min(5000, 300 * 2 ** retries++);
          timer = window.setTimeout(connect, delay);
        }
      };
    };

    const resize = new ResizeObserver(() => {
      if (host.current?.offsetParent) fitter.fit();
    });
    // Measure with the real font; a fallback font would leave the glyph grid misaligned.
    void Promise.all([
      document.fonts.load(`400 14px ${TERMINAL_FONT}`),
      document.fonts.load(`700 14px ${TERMINAL_FONT}`),
    ])
      .catch(() => undefined)
      .then(() => {
        if (disposed || !host.current) return;
        term.open(host.current);
        try {
          const webgl = new WebglAddon();
          webgl.onContextLoss(() => webgl.dispose());
          term.loadAddon(webgl);
        } catch {
          // The DOM renderer remains when WebGL is unavailable.
        }
        if (host.current.offsetParent) fitter.fit();
        resize.observe(host.current);
        connect();
      });
    return () => {
      disposed = true;
      window.clearTimeout(timer);
      resize.disconnect();
      socket?.close();
      term.dispose();
      terminal.current = null;
    };
  }, [session.id]);

  useEffect(() => {
    if (terminal.current) terminal.current.options.theme = terminalTheme(theme);
  }, [theme]);
  useEffect(() => {
    const term = terminal.current;
    if (!term) return;
    term.options.fontSize = fontSize;
    if (host.current?.offsetParent) fit.current?.fit();
  }, [fontSize]);
  useEffect(() => {
    if (!active) return;
    const frame = requestAnimationFrame(() => {
      if (host.current?.offsetParent) fit.current?.fit();
    });
    return () => cancelAnimationFrame(frame);
  }, [active]);

  const decorations = {
    matchBackground: theme === "light" ? "#fff3b0" : "#ffd34333",
    matchOverviewRuler: "#ffd343",
    activeMatchBackground: theme === "light" ? "#ffd343" : "#ffd34388",
    activeMatchColorOverviewRuler: "#ffd343",
  };
  const find = (forward: boolean, value = query) => {
    if (!value) return search.current?.clearDecorations();
    const options = { decorations, incremental: forward };
    if (forward) search.current?.findNext(value, options);
    else search.current?.findPrevious(value, options);
  };
  const closeFind = () => {
    setFinding(false);
    search.current?.clearDecorations();
    terminal.current?.focus();
  };
  const ended = !session.alive || link === "ended" || link === "lost";

  return (
    <div
      className={`console-view ${ended ? "ended" : ""}`}
      hidden={!active}
      role="tabpanel"
      id={`console-${session.id}`}
      aria-labelledby={`console-tab-${session.id}`}
    >
      <div className="console-surface" ref={host} />
      {finding && (
        <div className="console-find" role="search">
          <input
            ref={findInput}
            value={query}
            aria-label="Find in terminal"
            placeholder="Find"
            spellCheck={false}
            onChange={(event) => {
              setQuery(event.target.value);
              find(true, event.target.value);
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter") find(!event.shiftKey);
              if (event.key === "Escape") closeFind();
            }}
          />
          <button className="icon-btn" aria-label="Previous match" onClick={() => find(false)}>
            <ArrowUp size={14} />
          </button>
          <button className="icon-btn" aria-label="Next match" onClick={() => find(true)}>
            <ArrowDown size={14} />
          </button>
          <button className="icon-btn" aria-label="Close find" onClick={closeFind}>
            <X size={14} />
          </button>
        </div>
      )}
      {link === "connecting" && (
        <div className="console-pill" role="status">
          <LoaderCircle size={13} className="spin" /> Starting shell
        </div>
      )}
      {link === "reconnecting" && session.alive && (
        <div className="console-pill" role="status">
          <LoaderCircle size={13} className="spin" /> Reconnecting
        </div>
      )}
      {ended && (onRestart || onClose) && (
        <div className="console-ended" role="status">
          <p>
            <strong>
              {link === "lost" && session.alive
                ? "This shell is no longer available."
                : (endedText ?? "The shell exited.")}
            </strong>
            <span>Your workspace files are unchanged.</span>
          </p>
          <div className="row">
            {onRestart && (
              <button className="btn primary sm" onClick={onRestart}>
                <Plus size={15} /> New shell
              </button>
            )}
            {onClose && (
              <button className="btn sm" onClick={onClose}>
                Close tab
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
