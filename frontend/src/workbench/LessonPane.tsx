import { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  CircleCheck,
  Compass,
  Eye,
  FlaskConical,
  Lightbulb,
  ListChecks,
  Map as MapIcon,
  RotateCcw,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import { api } from "../api";
import { Markdown } from "../components/Markdown";
import { useApp } from "../context";
import { learnPath, navigate } from "../router";
import type { Activity, Stage } from "../types";
import { ChecksPanel, type CheckRun } from "./ChecksPanel";

export type LessonTab = "learn" | "task" | "checks";

function Prediction({
  activity,
  onAnswered,
}: {
  activity: Activity;
  onAnswered: (activity: Activity) => void;
}) {
  const { fail } = useApp();
  const prediction = activity.prediction!;
  const [choice, setChoice] = useState<number | null>(null);
  const [result, setResult] = useState<{
    correct: boolean;
    explanation: string | null;
  } | null>(prediction.answered ? { correct: true, explanation: prediction.explanation } : null);
  const answer = async (index: number) => {
    setChoice(index);
    try {
      const outcome = await api<{
        correct: boolean;
        explanation: string | null;
        flags: Activity["stages"];
      }>(`/activities/${encodeURIComponent(activity.id)}/prediction`, {
        choice: index,
      });
      setResult(outcome);
      onAnswered({
        ...activity,
        stages: outcome.flags,
        completed: outcome.flags.completed,
      });
    } catch (error) {
      fail(error);
    }
  };
  return (
    <section className="prediction card">
      <header>
        <Sparkles size={16} />
        <span className="eyebrow">Check your understanding · optional</span>
      </header>
      <p className="prediction-prompt">{prediction.prompt}</p>
      <div className="choices" role="radiogroup" aria-label="Answer choices">
        {prediction.choices.map((text, index) => {
          const chosen = choice === index;
          const state = chosen && result ? (result.correct ? "right" : "wrong") : "";
          return (
            <button
              key={index}
              role="radio"
              aria-checked={chosen}
              className={`choice ${state}`}
              onClick={() => void answer(index)}
            >
              <span className="choice-letter">{String.fromCharCode(65 + index)}</span>
              <span>{text}</span>
            </button>
          );
        })}
      </div>
      {result && (
        <p className={`prediction-feedback ${result.correct ? "right" : "wrong"}`} role="status">
          {result.correct
            ? result.explanation
            : "Not quite. Review the worked example above, then choose again."}
        </p>
      )}
    </section>
  );
}

export function LessonPane({
  activity,
  stage,
  tab,
  setTab,
  run,
  runKey,
  onActivity,
  onHint,
  onReference,
  onCheck,
  onAdvance,
  advanceLabel,
  onReset,
}: {
  activity: Activity;
  stage: Stage;
  tab: LessonTab;
  setTab: (tab: LessonTab) => void;
  run: CheckRun;
  runKey: number;
  onActivity: (activity: Activity) => void;
  onHint: () => void;
  onReference: () => void;
  onCheck: () => void;
  onAdvance?: () => void;
  advanceLabel?: string;
  onReset: () => void;
}) {
  const { catalog } = useApp();
  const scroller = useRef<HTMLDivElement>(null);
  const positions = useRef<Record<string, number>>({});
  const chapter = catalog.chapters.find((item) => item.id === activity.chapter.id);
  const finished = Object.values(run.cases).filter((item) => item.status === "finished");
  const passed = finished.filter((item) => item.passed).length;
  const isBuild = stage.stage === "build";

  // Each tab keeps its own reading position.
  useEffect(() => {
    const element = scroller.current;
    if (element) element.scrollTop = positions.current[`${activity.id}:${tab}`] ?? 0;
  }, [tab, activity.id]);

  return (
    <section className="lesson-pane" aria-label="Lesson">
      <nav className="lesson-tabs" role="tablist" aria-label="Lesson sections">
        {(
          [
            ["learn", "Learn", BookOpen],
            ["task", isBuild ? activity.build_label : "Repair", ListChecks],
            ["checks", "Checks", FlaskConical],
          ] as const
        ).map(([id, label, Icon]) => (
          <button
            key={id}
            role="tab"
            aria-selected={tab === id}
            className={tab === id ? "on" : ""}
            onClick={() => setTab(id)}
          >
            <Icon size={15} />
            {label}
            {id === "checks" && finished.length > 0 && (
              <span className={`tab-count ${passed === finished.length ? "ok" : "bad"}`}>
                {passed}/{stage.check_count}
              </span>
            )}
            {id === "checks" && run.running && <span className="tab-pulse" />}
          </button>
        ))}
      </nav>
      <div
        className="lesson-scroll"
        ref={scroller}
        onScroll={(event) => {
          positions.current[`${activity.id}:${tab}`] = event.currentTarget.scrollTop;
        }}
      >
        {tab === "learn" && (
          <article className="lesson-article">
            <div className="eyebrow">
              {activity.milestone ? "Game milestone" : "Lesson"} · Chapter {chapter?.number} ·{" "}
              {activity.chapter.title} · {activity.minutes} min
            </div>
            <h1>{activity.title}</h1>
            <p className="lede">{activity.subtitle}</p>
            {activity.updated && (
              <div className="callout warn">
                <TriangleAlert size={16} />
                <div>
                  This exercise was updated. Your previous draft is kept. Reset this stage to start
                  from the new version.
                  <button className="btn sm" onClick={onReset}>
                    <RotateCcw size={13} /> Reset this stage
                  </button>
                </div>
              </div>
            )}
            {activity.missing.length > 0 && (
              <div className="callout">
                <MapIcon size={16} />
                <div>
                  Useful preparation:{" "}
                  {activity.missing.map((item, index) => (
                    <span key={item.id}>
                      {index > 0 && ", "}
                      <a
                        href={learnPath(item.id)}
                        onClick={(event) => {
                          event.preventDefault();
                          navigate(learnPath(item.id));
                        }}
                      >
                        {item.title}
                      </a>
                    </span>
                  ))}
                  . You can continue now or revisit these later.
                </div>
              </div>
            )}
            {activity.origin && (
              <div className="callout game">
                <Compass size={16} />
                <div>{activity.origin}</div>
              </div>
            )}
            {activity.brief && <Markdown text={activity.brief} className="brief" />}
            <Markdown text={activity.body} />
            {activity.connection && (
              <div className="callout game">
                <Compass size={16} />
                <div>
                  <strong>Your game.</strong> Each chapter ends by extending Lantern Reach, the text
                  adventure you build across the course. This lesson helps you {activity.connection}
                </div>
              </div>
            )}
            {activity.prediction && <Prediction activity={activity} onAnswered={onActivity} />}
            <button className="btn primary next-step" onClick={() => setTab("task")}>
              Start the {isBuild ? activity.build_label : "Repair"} exercise{" "}
              <ArrowRight size={15} />
            </button>
          </article>
        )}
        {tab === "task" && (
          <article className="lesson-article">
            <div className="stage-steps">
              <span className={`step ${isBuild ? "on" : "done"}`}>
                {activity.stages.build.passed ? <CircleCheck size={14} /> : "1"}
                {activity.build_label}
              </span>
              <span className="step-line" />
              <span
                className={`step ${!isBuild ? "on" : activity.stages.repair.passed ? "done" : ""}`}
              >
                {activity.stages.repair.passed ? <CircleCheck size={14} /> : "2"} Repair
              </span>
            </div>
            <h2 className="task-title">
              {isBuild
                ? activity.milestone
                  ? "Extend your game"
                  : "Write it from scratch"
                : "Investigate and fix a program"}
            </h2>
            {stage.guidance && <p className="pace">{stage.guidance}</p>}
            <Markdown text={stage.instructions} className="instructions" />
            <section className="aid card">
              <header>
                <Lightbulb size={16} />
                <span className="eyebrow">Hints</span>
                <span className="muted small">
                  {stage.hints.revealed.length} of {stage.hints.total}
                </span>
              </header>
              {stage.hints.revealed.length ? (
                <ol className="hints">
                  {stage.hints.revealed.map((hint, index) => (
                    <li key={index}>{hint}</li>
                  ))}
                </ol>
              ) : (
                <p className="muted">Stuck? Reveal one hint at a time.</p>
              )}
              <div className="row">
                <button
                  className="btn sm"
                  onClick={onHint}
                  disabled={stage.hints.revealed.length >= stage.hints.total}
                >
                  <Lightbulb size={14} />
                  {stage.hints.revealed.length >= stage.hints.total
                    ? "All hints shown"
                    : `Show hint ${stage.hints.revealed.length + 1}`}
                </button>
                <button className="btn sm ghost" onClick={onReference}>
                  <Eye size={14} />{" "}
                  {stage.reference_seen ? "View reference again" : "Reveal reference"}
                </button>
              </div>
            </section>
            <button className="btn primary next-step" onClick={onCheck}>
              <CircleCheck size={15} /> Check my {isBuild ? activity.build_label : "repair"}
            </button>
          </article>
        )}
        {tab === "checks" && (
          <div className="lesson-article">
            <ChecksPanel
              key={runKey}
              run={run}
              total={stage.check_count}
              label={isBuild ? activity.build_label : "Repair"}
              onCheck={onCheck}
              onAdvance={onAdvance}
              advanceLabel={advanceLabel}
            />
          </div>
        )}
      </div>
    </section>
  );
}
