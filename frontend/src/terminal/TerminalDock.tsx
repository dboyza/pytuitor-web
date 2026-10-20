import { useCallback, useEffect, useImperativeHandle, useRef, useState, type Ref } from "react";
import {
  Eraser,
  FolderOpen,
  Maximize2,
  Minimize2,
  Minus,
  Plus,
  Search,
  SquareTerminal,
  X,
} from "lucide-react";
import { api } from "../api";
import { mod, useApp } from "../context";
import type { ConsoleSession, StageName } from "../types";
import { ConsoleView, type ConsoleHandle } from "./ConsoleView";

export type DockHandle = { run: () => Promise<void>; focus: () => void };
const SIZES = [11, 12, 13, 14, 15, 16, 18, 20];

function stored(key: string, fallback: number) {
  try {
    const value = Number(localStorage.getItem(key));
    return SIZES.includes(value) ? value : fallback;
  } catch {
    return fallback;
  }
}

// Start shells at the pane's real size; a wider guess makes zsh's line-end marker wrap.
function paneSize(body: HTMLElement | null, fontSize: number) {
  if (!body?.clientWidth) return { cols: 80, rows: 24 };
  return {
    cols: Math.max(20, Math.floor((body.clientWidth - 28) / (fontSize * 0.6)) - 1),
    rows: Math.max(5, Math.floor((body.clientHeight - 16) / Math.ceil(fontSize * 1.3))),
  };
}

export function TerminalDock({
  lessonId,
  stage,
  workspace,
  runCommand,
  maximized,
  onMaximize,
  ref,
}: {
  lessonId: string;
  stage: StageName;
  workspace: string;
  runCommand: string;
  maximized: boolean;
  onMaximize: () => void;
  ref?: Ref<DockHandle>;
}) {
  const { theme, fail, toast } = useApp();
  const key = `${lessonId}/${stage}`;
  const [sessions, setSessions] = useState<ConsoleSession[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [titles, setTitles] = useState<Record<string, string>>({});
  const [fontSize, setFontSize] = useState(() => stored("pytuitor-terminal-size", 13));
  const [dismissed, setDismissed] = useState(false);
  const handles = useRef(new Map<string, ConsoleHandle>());
  const body = useRef<HTMLDivElement>(null);
  const opening = useRef<Promise<ConsoleSession> | null>(null);
  const current =
    sessions.find((item) => item.id === selected) ??
    sessions.filter((item) => item.alive).at(-1) ??
    sessions.at(-1);

  const mineOf = useCallback(
    (all: ConsoleSession[]) =>
      all.filter((item) => item.key === key).sort((a, b) => a.number - b.number),
    [key],
  );
  const reload = useCallback(async () => {
    const mine = mineOf(await api<ConsoleSession[]>("/consoles"));
    setSessions(mine);
    return mine;
  }, [mineOf]);

  const open = useCallback(
    (fresh: boolean) => {
      // Concurrent callers share one request, so Run never opens two shells at once.
      opening.current ??= api<ConsoleSession>(
        `/activities/${encodeURIComponent(lessonId)}/stages/${stage}/consoles`,
        { ...paneSize(body.current, fontSize), fresh },
      ).finally(() => {
        opening.current = null;
      });
      return opening.current.then(async (created) => {
        await reload();
        setSelected(created.id);
        setDismissed(false);
        return created;
      });
    },
    [lessonId, stage, fontSize, reload],
  );

  useEffect(() => {
    let alive = true;
    api<ConsoleSession[]>("/consoles")
      .then((all) => {
        if (!alive) return;
        const mine = mineOf(all);
        setSessions(mine);
        if (!mine.some((item) => item.alive)) return open(false);
      })
      .catch(fail);
    return () => {
      alive = false;
    };
    // The dock remounts for each stage, so this runs once per workspace.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  useEffect(() => {
    try {
      localStorage.setItem("pytuitor-terminal-size", String(fontSize));
    } catch {
      // The size simply resets next time.
    }
  }, [fontSize]);

  useImperativeHandle(ref, () => ({
    focus: () => current && handles.current.get(current.id)?.focus(),
    run: async () => {
      const target = current?.alive ? current : await open(false);
      await api(`/consoles/${target.id}/run`, { lesson: lessonId });
      setSelected(target.id);
      requestAnimationFrame(() => handles.current.get(target.id)?.focus());
    },
  }));

  const close = async (session: ConsoleSession) => {
    if (sessions.length === 1) setDismissed(true);
    try {
      await api(`/consoles/${session.id}/close`, {});
      await reload();
    } catch (error) {
      fail(error);
    }
  };

  const resize = (step: number) =>
    setFontSize(
      (size) => SIZES[Math.max(0, Math.min(SIZES.length - 1, SIZES.indexOf(size) + step))],
    );

  return (
    <section className="dock" aria-label="Terminal">
      <header className="dock-bar">
        <div className="dock-tabs" role="tablist" aria-label="Shells">
          {sessions.map((session, index) => (
            <button
              key={session.id}
              role="tab"
              id={`console-tab-${session.id}`}
              className={`dock-tab ${current?.id === session.id ? "selected" : ""}`}
              aria-selected={current?.id === session.id}
              aria-controls={`console-${session.id}`}
              tabIndex={current?.id === session.id ? 0 : -1}
              onClick={() => {
                setSelected(session.id);
                handles.current.get(session.id)?.focus();
              }}
              onKeyDown={(event) => {
                const next = {
                  ArrowRight: (index + 1) % sessions.length,
                  ArrowLeft: (index - 1 + sessions.length) % sessions.length,
                }[event.key];
                if (event.key === "Delete") void close(session);
                if (next === undefined) return;
                event.preventDefault();
                setSelected(sessions[next].id);
                document.getElementById(`console-tab-${sessions[next].id}`)?.focus();
              }}
            >
              <span className={`dot ${session.alive ? "live" : ""}`} aria-hidden="true" />
              <SquareTerminal size={13} aria-hidden="true" />
              <span>Terminal {session.number}</span>
              {titles[session.id] && session.alive && (
                <span className="dock-title">{titles[session.id]}</span>
              )}
              <span
                className="dock-close"
                aria-hidden="true"
                title="Close (Delete)"
                onClick={(event) => {
                  event.stopPropagation();
                  void close(session);
                }}
              >
                <X size={12} />
              </span>
            </button>
          ))}
          <button
            className="icon-btn"
            aria-label="Open another shell"
            title={`New shell (Ctrl+Shift+\`)`}
            onClick={() => void open(true).catch(fail)}
          >
            <Plus size={15} />
          </button>
        </div>
        <div className="dock-actions">
          <button
            className="workspace-chip"
            title={`${workspace}\nClick to copy this folder's path`}
            onClick={() =>
              navigator.clipboard
                .writeText(workspace)
                .then(() => toast("Workspace path copied."))
                .catch(() => toast("Select and copy the path from the tooltip instead.", "error"))
            }
          >
            <FolderOpen size={13} aria-hidden="true" />
            <span>{workspace.split(/[\\/]/).slice(-2).join("/")}</span>
          </button>
          <div className="stepper" role="group" aria-label="Terminal text size">
            <button
              className="icon-btn"
              aria-label="Smaller text"
              disabled={fontSize === SIZES[0]}
              onClick={() => resize(-1)}
            >
              <Minus size={13} />
            </button>
            <output aria-live="polite">{fontSize}</output>
            <button
              className="icon-btn"
              aria-label="Larger text"
              disabled={fontSize === SIZES.at(-1)}
              onClick={() => resize(1)}
            >
              <Plus size={13} />
            </button>
          </div>
          <button
            className="icon-btn"
            aria-label="Find in terminal"
            title={`Find (${mod === "⌘" ? "⌘F" : "Ctrl+Shift+F"})`}
            disabled={!current}
            onClick={() => current && handles.current.get(current.id)?.find()}
          >
            <Search size={14} />
          </button>
          <button
            className="icon-btn"
            aria-label="Clear the terminal"
            title="Clear scrollback"
            disabled={!current}
            onClick={() => current && handles.current.get(current.id)?.clear()}
          >
            <Eraser size={14} />
          </button>
          <button
            className="icon-btn"
            aria-label={maximized ? "Restore the editor" : "Maximize the terminal"}
            title={maximized ? "Restore" : "Maximize"}
            onClick={onMaximize}
          >
            {maximized ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </header>
      <div className="dock-body" ref={body}>
        {sessions.map((session) => (
          <ConsoleView
            key={session.id}
            ref={(handle) => {
              if (handle) handles.current.set(session.id, handle);
              else handles.current.delete(session.id);
            }}
            session={session}
            active={current?.id === session.id}
            theme={theme}
            fontSize={fontSize}
            onTitle={(title) => setTitles((all) => ({ ...all, [session.id]: title }))}
            onEnded={() => void reload()}
            onRestart={() => void open(true).catch(fail)}
            onClose={() => void close(session)}
          />
        ))}
        {!sessions.length && (
          <div className="dock-empty">
            <SquareTerminal size={28} strokeWidth={1.5} />
            <p>
              {dismissed
                ? "No shell is open for this workspace."
                : "Starting a shell in your workspace…"}
            </p>
            {dismissed && (
              <button className="btn primary sm" onClick={() => void open(true).catch(fail)}>
                <Plus size={14} /> Open a terminal
              </button>
            )}
            <code className="muted">{runCommand}</code>
          </div>
        )}
      </div>
    </section>
  );
}
