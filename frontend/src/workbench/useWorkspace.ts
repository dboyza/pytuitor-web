import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { Flags, Poll, Stage, StageName } from "../types";

export type SaveStatus = "saved" | "saving" | "error";
export type Preview = { name: string; content: string };

const SAVE_DELAY = 400;
const POLL_INTERVAL = 1500;

/**
 * Keeps the editor's files in step with the stage's folder on disk. Edits autosave per file;
 * edits made in the terminal arrive by polling and replace only files without unsaved changes.
 * The caller passes each new stage payload to load(); later local changes never reload it.
 */
export function useWorkspace(
  lessonId: string,
  stage: Stage | null,
  onFlags: (flags: Flags) => void,
  onError: (error: unknown) => void,
  onExternal: (name: string) => void,
) {
  const stageName: StageName | undefined = stage?.stage;
  const base = `/activities/${encodeURIComponent(lessonId)}/stages/${stageName}`;
  const [contents, setContents] = useState<Record<string, string>>({});
  const [order, setOrder] = useState<string[]>([]);
  const [required, setRequired] = useState<Set<string>>(new Set());
  const [untracked, setUntracked] = useState<Stage["untracked"]>([]);
  const [active, setActive] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [status, setStatus] = useState<SaveStatus>("saved");
  const latest = useRef<Record<string, string>>({});
  const saved = useRef<Record<string, string>>({});
  // The server's fingerprint of each file as this tab last saw it.
  const hashes = useRef<Record<string, string>>({});
  const timers = useRef(new Map<string, number>());
  const inflight = useRef(new Map<string, Promise<void>>());
  const callbacks = useRef({ onFlags, onError, onExternal });
  useEffect(() => {
    callbacks.current = { onFlags, onError, onExternal };
  });

  const load = useCallback((data: Stage) => {
    for (const timer of timers.current.values()) window.clearTimeout(timer);
    timers.current.clear();
    const files = Object.fromEntries(data.files.map((file) => [file.name, file.content]));
    latest.current = { ...files };
    saved.current = { ...files };
    hashes.current = Object.fromEntries(data.files.map((file) => [file.name, file.hash]));
    setContents(files);
    setOrder(data.files.map((file) => file.name));
    setRequired(new Set(data.files.filter((file) => file.required).map((file) => file.name)));
    setUntracked(data.untracked);
    setActive(data.view.active_file);
    setPreview(null);
    setStatus("saved");
  }, []);

  const refreshStatus = () => {
    const busy = timers.current.size > 0 || inflight.current.size > 0;
    setStatus((value) => (busy ? "saving" : value === "error" ? "error" : "saved"));
  };

  const save = useCallback(
    (name: string) => {
      timers.current.delete(name);
      const content = latest.current[name];
      if (content === undefined || content === saved.current[name]) {
        refreshStatus();
        return Promise.resolve();
      }
      const previous = inflight.current.get(name) ?? Promise.resolve();
      const request = previous
        .then(() => api<{ hash: string; flags: Flags }>(`${base}/file`, { name, content }, "PUT"))
        .then((result) => {
          saved.current[name] = content;
          hashes.current[name] = result.hash;
          callbacks.current.onFlags(result.flags);
          setStatus("saved");
        })
        .catch((error) => {
          setStatus("error");
          callbacks.current.onError(error);
        })
        .finally(() => {
          if (inflight.current.get(name) === request) inflight.current.delete(name);
          refreshStatus();
        });
      inflight.current.set(name, request);
      setStatus("saving");
      return request;
    },
    [base],
  );

  const edit = useCallback(
    (name: string, content: string) => {
      if (latest.current[name] === content) return;
      latest.current[name] = content;
      setContents((all) => ({ ...all, [name]: content }));
      window.clearTimeout(timers.current.get(name));
      timers.current.set(
        name,
        window.setTimeout(() => void save(name), SAVE_DELAY),
      );
      setStatus("saving");
    },
    [save],
  );

  /** Write every pending edit now; Run and Check call this first. */
  const flush = useCallback(async () => {
    const names = [...timers.current.keys()];
    for (const name of names) window.clearTimeout(timers.current.get(name));
    await Promise.all([...names.map(save), ...inflight.current.values()]);
  }, [save]);

  useEffect(() => {
    if (!stageName) return;
    let stopped = false;
    const tick = async () => {
      if (document.hidden) return;
      try {
        const poll = await api<Poll>(`${base}/poll`);
        if (stopped) return;
        const dirty = (name: string) =>
          timers.current.has(name) ||
          inflight.current.has(name) ||
          latest.current[name] !== saved.current[name];
        const updates: Record<string, string> = {};
        const adopt = (name: string, content: string, external: boolean) => {
          updates[name] = content;
          latest.current[name] = content;
          saved.current[name] = content;
          hashes.current[name] = poll.files[name];
          if (external) callbacks.current.onExternal(name);
        };
        for (const [name, hash] of Object.entries(poll.files)) {
          if (dirty(name) || hash === hashes.current[name]) continue;
          if (name in poll.changed) adopt(name, poll.changed[name], true);
          else {
            // Another tab saved this file; fetch the current text.
            const file = await api<{ content: string; hash: string }>(
              `${base}/file?name=${encodeURIComponent(name)}`,
            );
            if (stopped) return;
            if (!dirty(name) && file.hash === hash) adopt(name, file.content, false);
          }
        }
        const removed = Object.keys(latest.current).filter((name) => !(name in poll.files));
        for (const name of removed) {
          delete latest.current[name];
          delete saved.current[name];
          delete hashes.current[name];
        }
        if (Object.keys(updates).length || removed.length) {
          setContents({ ...latest.current });
          setOrder((names) => [
            ...names.filter((name) => name in latest.current),
            ...Object.keys(updates).filter((name) => !names.includes(name)),
          ]);
        }
        setUntracked((previous) =>
          JSON.stringify(previous) === JSON.stringify(poll.untracked) ? previous : poll.untracked,
        );
        callbacks.current.onFlags(poll.flags);
      } catch {
        // A missed poll is retried on the next tick.
      }
    };
    const timer = window.setInterval(() => void tick(), POLL_INTERVAL);
    return () => {
      stopped = true;
      window.clearInterval(timer);
    };
  }, [base, stageName]);

  useEffect(() => {
    const leave = (event: BeforeUnloadEvent) => {
      if (timers.current.size || inflight.current.size) event.preventDefault();
    };
    window.addEventListener("beforeunload", leave);
    return () => window.removeEventListener("beforeunload", leave);
  }, []);

  const select = useCallback(
    (name: string) => {
      setPreview(null);
      setActive(name);
      void api(`${base}/view`, { name }).catch(() => undefined);
    },
    [base],
  );

  const showPreview = useCallback(
    async (name: string) => {
      try {
        const result = await api<{ content: string }>(
          `${base}/preview?name=${encodeURIComponent(name)}`,
        );
        setPreview({ name, content: result.content });
      } catch (error) {
        callbacks.current.onError(error);
      }
    },
    [base],
  );

  return {
    load,
    contents,
    order,
    required,
    untracked,
    active: active in contents ? active : (order[0] ?? ""),
    preview,
    status,
    edit,
    flush,
    select,
    showPreview,
    closePreview: () => setPreview(null),
  };
}

export type Workspace = ReturnType<typeof useWorkspace>;
