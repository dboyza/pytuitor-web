import { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  Check,
  ChevronRight,
  Code2,
  Compass,
  Download,
  Ellipsis,
  Gamepad2,
  Keyboard,
  Lock,
  NotebookPen,
  RotateCcw,
  SquareTerminal,
} from "lucide-react";
import { api, download, streamEvents } from "../api";
import { isMod, useApp } from "../context";
import { Confetti, Menu, PlayDialog, Splitter } from "../components/extras";
import { Dialog, Spinner, TopBarSlot } from "../components/ui";
import { learnPath, navigate } from "../router";
import { TerminalDock, type DockHandle } from "../terminal/TerminalDock";
import type { Activity, CheckCase, Flags, Stage, StageName } from "../types";
import { idleRun, type CheckRun } from "./ChecksPanel";
import { EditorPane } from "./EditorPane";
import { LessonPane, type LessonTab } from "./LessonPane";
import { ReferenceDialog } from "./ReferenceDialog";
import { useWorkspace } from "./useWorkspace";

type Layout = { lesson: number; editor: number };
const NARROW = 980;

function storedLayout(): Layout {
  try {
    const value = JSON.parse(localStorage.getItem("pytuitor-layout") ?? "{}");
    return {
      lesson: Math.min(0.6, Math.max(0.24, Number(value.lesson) || 0.38)),
      editor: Math.min(0.8, Math.max(0.2, Number(value.editor) || 0.58)),
    };
  } catch {
    return { lesson: 0.38, editor: 0.58 };
  }
}

function reportRun(stage: Stage): CheckRun {
  if (!stage.report) return idleRun;
  const cases: Record<number, CheckCase> = {};
  for (const item of stage.report.cases) cases[item.number] = item;
  return { ...idleRun, cases, stale: !stage.report.current };
}

export function Workbench({ id }: { id: string }) {
  const app = useApp();
  const { fail, toast, refresh, confirm, catalog } = app;
  const [activity, setActivity] = useState<Activity | null>(null);
  const [stage, setStage] = useState<Stage | null>(null);
  const [tab, setTab] = useState<LessonTab>("learn");
  const [run, setRun] = useState<CheckRun>(idleRun);
  const [runKey, setRunKey] = useState(0);
  const [reference, setReference] = useState<Record<string, string> | null>(null);
  const [noting, setNoting] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [celebrate, setCelebrate] = useState(0);
  const [layout, setLayout] = useState(storedLayout);
  const [maximized, setMaximized] = useState(false);
  const [narrow, setNarrow] = useState(() => window.innerWidth < NARROW);
  const [pane, setPane] = useState<"lesson" | "code" | "terminal">("lesson");
  const dock = useRef<DockHandle>(null);
  const body = useRef<HTMLDivElement>(null);
  const right = useRef<HTMLDivElement>(null);
  const abort = useRef<AbortController | null>(null);
  const base = `/activities/${encodeURIComponent(id)}`;

  const applyFlags = useCallback((flags: Flags) => {
    setActivity((current) =>
      current &&
      (JSON.stringify(current.stages) !== JSON.stringify(flags) ||
        current.completed !== flags.completed)
        ? { ...current, stages: flags, completed: flags.completed }
        : current,
    );
  }, []);

  const workspace = useWorkspace(id, stage, applyFlags, fail, (name) =>
    toast(`${name} changed in the terminal, so the editor now shows it.`),
  );
  const { load } = workspace;

  // A fresh stage payload from the server replaces the editor's files and the check report.
  const applyStage = useCallback(
    (data: Stage, report = true) => {
      setStage(data);
      load(data);
      if (report) {
        setRun(reportRun(data));
        setRunKey((key) => key + 1);
      }
    },
    [load],
  );

  useEffect(() => {
    let alive = true;
    api<Activity>(`${base}/open`, {})
      .then(async (opened) => {
        if (!alive) return;
        setActivity(opened);
        const data = await api<Stage>(`${base}/stages/${opened.stage}`);
        if (!alive) return;
        applyStage(data);
        void refresh();
      })
      .catch((error) => {
        fail(error);
        navigate("/", true);
      });
    return () => {
      alive = false;
      abort.current?.abort();
    };
    // Opening a lesson happens once; the page remounts for another lesson.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    const resize = () => setNarrow(window.innerWidth < NARROW);
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("pytuitor-layout", JSON.stringify(layout));
    } catch {
      // The layout resets next time.
    }
  }, [layout]);

  const runProgram = useCallback(async () => {
    if (!stage) return;
    if (narrow) setPane("terminal");
    setMaximized(false);
    try {
      await workspace.flush();
      await dock.current?.run();
    } catch (error) {
      fail(error);
    }
  }, [stage, workspace, fail, narrow]);

  const check = useCallback(async () => {
    if (!stage || !activity || run.running) return;
    setTab("checks");
    if (narrow) setPane("lesson");
    setRunKey((key) => key + 1);
    setRun({ ...idleRun, running: true });
    const controller = new AbortController();
    abort.current = controller;
    try {
      await workspace.flush();
      await streamEvents(
        `${base}/stages/${stage.stage}/check`,
        (event) => {
          if (event.type === "case")
            setRun((current) => ({
              ...current,
              cases: { ...current.cases, [event.case.number]: event.case },
            }));
          else if (event.type === "done") {
            const cases: Record<number, CheckCase> = {};
            for (const item of event.cases) cases[item.number] = item;
            setRun({ ...idleRun, cases, outcome: event });
            const wasComplete = activity.completed;
            applyFlags(event.flags);
            if (event.passed) setCelebrate((count) => count + (wasComplete ? 0 : 1));
            if (event.flags.completed && !wasComplete) void refresh();
          } else setRun({ ...idleRun, failure: event.detail });
        },
        controller.signal,
      );
    } catch (error) {
      if (!controller.signal.aborted) {
        setRun({ ...idleRun, failure: (error as Error).message });
      }
    } finally {
      setRun((current) => (current.running ? { ...current, running: false } : current));
    }
  }, [stage, activity, run.running, workspace, base, applyFlags, refresh, narrow]);

  const switchStage = useCallback(
    async (name: StageName) => {
      if (!activity || !stage || name === stage.stage) return;
      if (name === "repair" && !activity.stages.repair.unlocked) {
        toast(`Pass the ${activity.build_label} checks to unlock Repair.`);
        return;
      }
      try {
        await workspace.flush();
        const data = await api<Stage>(`${base}/stage`, { stage: name });
        setActivity({ ...activity, stage: name });
        applyStage(data);
        setTab("task");
      } catch (error) {
        fail(error);
      }
    },
    [activity, stage, workspace, base, toast, fail, applyStage],
  );

  const advance = useCallback(async () => {
    if (!activity || !stage) return;
    if (stage.stage === "build") return switchStage("repair");
    try {
      const { next } = await api<{ next: string | null }>(`${base}/next`, {});
      await refresh();
      if (next) navigate(learnPath(next));
      else {
        toast("Section complete. Choose another chapter in the syllabus.", "success");
        navigate("/syllabus");
      }
    } catch (error) {
      fail(error);
    }
  }, [activity, stage, base, switchStage, refresh, toast, fail]);

  const hint = async () => {
    if (!stage) return;
    try {
      const hints = await api<Stage["hints"]>(`${base}/stages/${stage.stage}/hint`, {});
      setStage({ ...stage, hints });
    } catch (error) {
      fail(error);
    }
  };

  const showReference = async () => {
    if (!stage) return;
    const proceed =
      stage.reference_seen ||
      (await confirm({
        title: "Reveal a reference solution?",
        body: "You'll see one correct approach. Your draft is not replaced. Trying one more hint first often teaches more.",
        confirm: "Reveal reference",
      }));
    if (!proceed) return;
    try {
      await workspace.flush();
      const result = await api<{ files: Record<string, string> }>(
        `${base}/stages/${stage.stage}/reference`,
        {},
      );
      setStage({ ...stage, reference_seen: true });
      setReference(result.files);
    } catch (error) {
      fail(error);
    }
  };

  const reset = async () => {
    if (!stage || !activity) return;
    const label = stage.stage === "build" ? activity.build_label : "Repair";
    const proceed = await confirm({
      title: `Reset the ${label} stage?`,
      body:
        stage.stage === "build"
          ? `Your current ${label} files are backed up to your exports folder, then the stage starts again${activity.milestone ? " from its base code" : " with a blank editor"}. Its terminal closes.`
          : "Your current Repair files are backed up to your exports folder, then the original broken program returns. Its terminal closes.",
      confirm: `Back up and reset`,
      danger: true,
    });
    if (!proceed) return;
    try {
      await workspace.flush();
      const data = await api<Stage>(`${base}/stages/${stage.stage}/reset`, {});
      applyStage(data);
      setActivity({
        ...activity,
        updated: false,
        stages: data.flags,
        completed: data.flags.completed,
      });
      toast(`Stage reset. Backup saved to ${data.backup}`, "success");
    } catch (error) {
      fail(error);
    }
  };

  const addFile = async (name: string, track = false) => {
    if (!stage) return false;
    try {
      await workspace.flush();
      const data = await api<Stage>(`${base}/stages/${stage.stage}/files`, {
        name,
        track,
      });
      applyStage(data, false);
      return true;
    } catch (error) {
      fail(error);
      return false;
    }
  };

  const removeFile = async (name: string) => {
    if (!stage) return;
    const proceed = await confirm({
      title: `Remove ${name}?`,
      body: "The whole workspace is backed up to your exports folder first.",
      confirm: "Back up and remove",
      danger: true,
    });
    if (!proceed) return;
    try {
      await workspace.flush();
      applyStage(
        await api<Stage>(`${base}/stages/${stage.stage}/files/remove`, {
          name,
        }),
        false,
      );
    } catch (error) {
      fail(error);
    }
  };

  useEffect(() => {
    const key = (event: KeyboardEvent) => {
      if (event.defaultPrevented) return;
      if (isMod(event) && event.key === "Enter") {
        event.preventDefault();
        if (event.shiftKey) void check();
        else void runProgram();
      } else if (event.ctrlKey && event.key === "`") {
        event.preventDefault();
        if (narrow) setPane("terminal");
        dock.current?.focus();
      } else if (isMod(event) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        void workspace.flush();
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [check, runProgram, workspace, narrow]);

  if (!activity || !stage) {
    return (
      <div className="page-loading">
        <Spinner size={22} />
      </div>
    );
  }

  const chapter = catalog.chapters.find((item) => item.id === activity.chapter.id);
  const passedHere =
    stage.stage === "build" ? activity.stages.build.passed : activity.stages.repair.passed;
  const advanceLabel = stage.stage === "build" ? "Continue to Repair" : "Next lesson";
  const lessonWidth = `${layout.lesson * 100}%`;

  return (
    <div className="workbench-page">
      <TopBarSlot>
        <nav className="crumbs" aria-label="Breadcrumb">
          <a
            href="/syllabus"
            onClick={(event) => {
              event.preventDefault();
              navigate("/syllabus");
            }}
          >
            Chapter {chapter?.number} · {activity.chapter.title}
          </a>
          <ChevronRight size={14} />
          <span className="current">{activity.title}</span>
          {activity.completed && (
            <span className="badge green">
              <Check size={11} /> Complete
            </span>
          )}
        </nav>
        <div className="stage-switch" role="tablist" aria-label="Exercise stage">
          {(["build", "repair"] as const).map((name, index) => {
            const flags = name === "build" ? activity.stages.build : activity.stages.repair;
            const locked = name === "repair" && !activity.stages.repair.unlocked;
            return (
              <button
                key={name}
                role="tab"
                aria-selected={stage.stage === name}
                className={`${stage.stage === name ? "on" : ""} ${flags.passed ? "passed" : ""}`}
                onClick={() => void switchStage(name)}
                title={locked ? `Pass ${activity.build_label} to unlock Repair` : undefined}
              >
                <span className="stage-num">
                  {flags.passed ? (
                    <Check size={11} strokeWidth={3} />
                  ) : locked ? (
                    <Lock size={10} />
                  ) : (
                    index + 1
                  )}
                </span>
                {name === "build" ? activity.build_label : "Repair"}
              </button>
            );
          })}
        </div>
        <button
          className={`btn sm ${passedHere ? "primary glow" : ""}`}
          disabled={!passedHere}
          onClick={() => void advance()}
          title={passedHere ? undefined : "Pass this stage's checks first"}
        >
          {stage.stage === "build" ? "Repair" : "Next"} <ArrowRight size={14} />
        </button>
        <Menu
          label="Lesson options"
          trigger={<Ellipsis size={17} />}
          items={[
            {
              label: "Note for next time",
              icon: <NotebookPen size={15} />,
              onSelect: () => setNoting(true),
            },
            {
              label: "Download workspace (.zip)",
              icon: <Download size={15} />,
              onSelect: () => download(`${base}/stages/${stage.stage}/export`),
            },
            ...(activity.milestone
              ? [
                  ...(activity.checkpoint
                    ? [
                        {
                          label: "Play your working version",
                          icon: <Gamepad2 size={15} />,
                          onSelect: () => setPlaying(true),
                        },
                      ]
                    : []),
                  {
                    label: "Your game overview",
                    icon: <Compass size={15} />,
                    onSelect: () => navigate("/game"),
                  },
                ]
              : []),
            {
              label: "Keyboard shortcuts",
              icon: <Keyboard size={15} />,
              onSelect: app.openShortcuts,
            },
            "divider",
            {
              label: `Reset ${stage.stage === "build" ? activity.build_label : "Repair"} stage…`,
              icon: <RotateCcw size={15} />,
              danger: true,
              onSelect: () => void reset(),
            },
          ]}
        />
      </TopBarSlot>

      {narrow && (
        <div className="pane-switch" role="tablist" aria-label="Workbench panes">
          {(
            [
              ["lesson", "Lesson", BookOpen],
              ["code", "Code", Code2],
              ["terminal", "Terminal", SquareTerminal],
            ] as const
          ).map(([value, label, Icon]) => (
            <button
              key={value}
              role="tab"
              aria-selected={pane === value}
              className={pane === value ? "on" : ""}
              onClick={() => setPane(value)}
            >
              <Icon size={15} /> {label}
            </button>
          ))}
        </div>
      )}

      <div
        ref={body}
        className={`workbench ${narrow ? `narrow show-${pane}` : ""} ${maximized ? "maximized" : ""}`}
        style={narrow ? undefined : { gridTemplateColumns: `${lessonWidth} 10px minmax(0, 1fr)` }}
      >
        <LessonPane
          activity={activity}
          stage={stage}
          tab={tab}
          setTab={setTab}
          run={run}
          runKey={runKey}
          onActivity={setActivity}
          onHint={() => void hint()}
          onReference={() => void showReference()}
          onCheck={() => void check()}
          onAdvance={passedHere ? () => void advance() : undefined}
          advanceLabel={advanceLabel}
          onReset={() => void reset()}
        />
        {!narrow && (
          <Splitter
            direction="row"
            label="Resize the lesson"
            onDrag={(x) => {
              const box = body.current!.getBoundingClientRect();
              const share = (x - box.left) / box.width;
              setLayout((value) => ({
                ...value,
                lesson: Math.min(0.6, Math.max(0.24, share)),
              }));
            }}
          />
        )}
        <div
          className="work-right"
          ref={right}
          style={
            narrow || maximized
              ? undefined
              : {
                  gridTemplateRows: `${layout.editor * 100}% 10px minmax(0, 1fr)`,
                }
          }
        >
          <EditorPane
            workspace={workspace}
            stage={stage}
            checking={run.running}
            fontSize={14}
            onRun={() => void runProgram()}
            onCheck={() => void check()}
            onAdd={(name) => addFile(name)}
            onRemove={(name) => void removeFile(name)}
            onTrack={(name) => void addFile(name, true)}
          />
          {!narrow && !maximized && (
            <Splitter
              direction="column"
              label="Resize the terminal"
              onDrag={(y) => {
                const box = right.current!.getBoundingClientRect();
                const share = (y - box.top) / box.height;
                setLayout((value) => ({
                  ...value,
                  editor: Math.min(0.8, Math.max(0.2, share)),
                }));
              }}
            />
          )}
          <TerminalDock
            key={stage.stage}
            ref={dock}
            lessonId={id}
            stage={stage.stage}
            workspace={stage.workspace}
            runCommand={stage.run}
            maximized={maximized}
            onMaximize={() => setMaximized(!maximized)}
          />
        </div>
      </div>

      {reference && (
        <ReferenceDialog
          files={reference}
          drafts={workspace.contents}
          entrypoint={stage.entrypoint}
          onClose={() => setReference(null)}
        />
      )}
      {noting && (
        <NoteDialog
          initial={activity.note}
          onClose={() => setNoting(false)}
          onSave={async (note) => {
            try {
              await api(`${base}/note`, { note });
              setActivity({ ...activity, note });
              setNoting(false);
              toast(note ? "Note saved for next time." : "Note cleared.", "success");
              void refresh();
            } catch (error) {
              fail(error);
            }
          }}
        />
      )}
      {playing && activity.checkpoint && (
        <PlayDialog
          checkpoint={activity.checkpoint}
          title={activity.title}
          onClose={() => setPlaying(false)}
        />
      )}
      {celebrate > 0 && <Confetti key={celebrate} />}
    </div>
  );
}

function NoteDialog({
  initial,
  onClose,
  onSave,
}: {
  initial: string;
  onClose: () => void;
  onSave: (note: string) => void;
}) {
  const [text, setText] = useState(initial);
  return (
    <Dialog
      title="Note for next time"
      onClose={onClose}
      footer={
        <>
          <button className="btn" onClick={onClose}>
            Cancel
          </button>
          <button className="btn primary" onClick={() => onSave(text)}>
            Save note
          </button>
        </>
      }
    >
      <p className="muted">Leave yourself a reminder. It appears on Home when you come back.</p>
      <textarea
        className="input"
        rows={4}
        maxLength={500}
        value={text}
        placeholder="Next: handle an empty list before computing the average."
        onChange={(event) => setText(event.target.value)}
      />
    </Dialog>
  );
}
