import { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  BellOff,
  BellRing,
  CalendarClock,
  CircleCheck,
  CircleX,
  Eye,
  Lightbulb,
  Repeat2,
} from "lucide-react";
import { api } from "../api";
import { CodeEditor } from "../components/CodeEditor";
import { CodeBlock, Markdown } from "../components/Markdown";
import { Kbd, Spinner, TopBarSlot } from "../components/ui";
import { isMod, mod, useApp } from "../context";
import { navigate } from "../router";
import type { CheckCase, ReviewChapter, ReviewSessionInfo, ReviewTask } from "../types";

export function Reviews() {
  const { fail, catalog } = useApp();
  const [data, setData] = useState<{
    paused: boolean;
    suggested: string | null;
    chapters: ReviewChapter[];
  } | null>(null);
  useEffect(() => {
    api<typeof data>("/reviews").then(setData).catch(fail);
  }, [fail]);
  if (!data) {
    return (
      <div className="page-loading">
        <Spinner size={22} />
      </div>
    );
  }
  const act = (path: string) => api<typeof data>(path, {}).then(setData).catch(fail);
  return (
    <div className="page reviews">
      <TopBarSlot>
        <nav className="crumbs">
          <span className="current">Review</span>
        </nav>
      </TopBarSlot>
      <header className="page-head">
        <div>
          <p className="eyebrow">Optional</p>
          <h1>A short return to earlier ideas</h1>
          <p className="muted">
            Three tasks per chapter: predict, repair, and write. Reviews never block Continue, and
            your course progress stays the same. Spacing grows as you succeed.
          </p>
        </div>
        <button className="btn" onClick={() => void act("/reviews/pause")}>
          {data.paused ? <BellRing size={15} /> : <BellOff size={15} />}
          {data.paused ? "Resume suggestions" : "Pause suggestions"}
        </button>
      </header>
      {catalog.sections.map((section) => {
        const chapters = data.chapters.filter((item) => item.section_id === section.id);
        return (
          <section key={section.id} className="review-section">
            <h2 className="section-title">{section.title}</h2>
            <div className="review-grid">
              {chapters.map((item) => (
                <article key={item.id} className={`review-card ${item.label.toLowerCase()}`}>
                  <header>
                    <span className={`chip ${item.label.toLowerCase()}`}>{item.label}</span>
                    <span
                      className="review-dots"
                      aria-label={`${item.passed} of ${item.total} passed`}
                    >
                      {Array.from({ length: item.total }, (_, index) => (
                        <span key={index} className={index < item.passed ? "on" : ""} />
                      ))}
                    </span>
                  </header>
                  <h3>{item.title}</h3>
                  <p className="muted small">
                    {item.finished
                      ? `Finished${item.due ? ` · next suggested ${new Date(item.due + "T00:00").toLocaleDateString()}` : ""}`
                      : item.started
                        ? "Resume your saved attempt."
                        : item.label === "Preview"
                          ? "Finish the chapter first, or preview it now."
                          : "About 6 to 10 minutes."}
                  </p>
                  <div className="row">
                    <button
                      className={`btn sm ${item.label === "Suggested" ? "primary" : ""}`}
                      onClick={() => navigate(`/review/${item.id}`)}
                    >
                      <Repeat2 size={14} />{" "}
                      {item.finished ? "Practice again" : item.started ? "Resume" : "Start"}
                    </button>
                    {item.label === "Suggested" && (
                      <button
                        className="btn sm ghost"
                        onClick={() => void act(`/reviews/${item.id}/defer`)}
                      >
                        <CalendarClock size={14} /> Tomorrow
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}

export function ReviewSession({ chapter }: { chapter: string }) {
  const { fail, toast, refresh } = useApp();
  const [session, setSession] = useState<ReviewSessionInfo | null>(null);
  const [task, setTask] = useState<ReviewTask | null>(null);
  const [code, setCode] = useState("");
  const [checking, setChecking] = useState(false);
  const [feedback, setFeedback] = useState<{
    passed: boolean;
    text: string;
    cases: CheckCase[];
    error?: string;
  } | null>(null);
  const [aid, setAid] = useState<{
    kind: "hint" | "reference";
    text: string;
  } | null>(null);
  const path = (index: number) => `/reviews/${chapter}/tasks/${index}`;
  const timer = useRef(0);

  const load = useCallback(
    async (index: number) => {
      const data = await api<ReviewTask>(path(index));
      setTask(data);
      setCode(data.code);
      setFeedback(data.passed ? { passed: true, text: "Passed previously.", cases: [] } : null);
      setAid(null);
    },
    // path depends only on chapter.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [chapter],
  );

  useEffect(() => {
    api<ReviewSessionInfo>(`/reviews/${chapter}/open`, {})
      .then(async (info) => {
        setSession(info);
        await load(info.index);
      })
      .catch((error) => {
        fail(error);
        navigate("/review", true);
      });
  }, [chapter, load, fail]);

  const save = async (body: { code?: string; choice?: number }) => {
    if (!task) return;
    try {
      await api(path(task.index), body, "PUT");
    } catch (error) {
      fail(error);
    }
  };

  const check = useCallback(async () => {
    if (!task || checking) return;
    setChecking(true);
    try {
      window.clearTimeout(timer.current);
      if (task.kind !== "predict") await api(path(task.index), { code }, "PUT");
      const result = await api<{
        passed: boolean;
        feedback: string;
        cases: CheckCase[];
        error: string;
      }>(path(task.index) + "/check", {});
      setFeedback({
        passed: result.passed,
        text: result.feedback,
        cases: result.cases,
        error: result.error,
      });
      if (result.passed && session) {
        setSession({
          ...session,
          tasks: session.tasks.map((item, index) =>
            index === task.index ? { ...item, passed: true } : item,
          ),
        });
        setTask({ ...task, passed: true });
      }
    } catch (error) {
      fail(error);
    } finally {
      setChecking(false);
    }
    // path depends only on chapter.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [task, checking, code, session, fail]);

  useEffect(() => {
    const key = (event: KeyboardEvent) => {
      if (!event.defaultPrevented && isMod(event) && event.key === "Enter") {
        event.preventDefault();
        void check();
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [check]);

  if (!session || !task) {
    return (
      <div className="page-loading">
        <Spinner size={22} />
      </div>
    );
  }

  const next = async () => {
    try {
      const result = await api<{
        finished: boolean;
        index?: number;
        due?: string;
      }>(path(task.index) + "/next", {});
      if (result.finished) {
        toast("Review complete. Your course progress is unchanged.", "success");
        void refresh();
        navigate("/review");
      } else {
        setSession({ ...session, index: result.index! });
        await load(result.index!);
      }
    } catch (error) {
      fail(error);
    }
  };
  const showAid = async (kind: "hint" | "reference") => {
    try {
      const result = await api<{ text: string }>(path(task.index) + `/${kind}`, {});
      setAid({ kind, text: result.text });
    } catch (error) {
      fail(error);
    }
  };

  return (
    <div className="page review-session">
      <TopBarSlot>
        <nav className="crumbs">
          <a
            href="/review"
            onClick={(event) => {
              event.preventDefault();
              navigate("/review");
            }}
          >
            Review
          </a>
          <span className="sep">/</span>
          <span className="current">{session.title}</span>
        </nav>
      </TopBarSlot>
      <div className="review-steps">
        {session.tasks.map((item, index) => (
          <span
            key={index}
            className={`step ${index === task.index ? "on" : ""} ${item.passed ? "done" : ""}`}
          >
            {item.passed ? <CircleCheck size={14} /> : index + 1}
            <span>
              {item.kind === "predict" ? "Predict" : item.kind === "debug" ? "Repair" : "Write"}
            </span>
          </span>
        ))}
      </div>
      <div className="review-body">
        <section className="review-prompt card">
          <p className="eyebrow">
            Task {task.index + 1} of {session.tasks.length} ·{" "}
            {task.kind === "predict" ? "Predict" : task.kind === "debug" ? "Repair" : "Write"}
          </p>
          <h1>{task.title}</h1>
          <Markdown text={task.prompt} />
          {task.kind === "predict" && (
            <div className="choices" role="radiogroup">
              {task.choices.map((text, index) => (
                <button
                  key={index}
                  role="radio"
                  aria-checked={task.choice === index}
                  className={`choice ${task.choice === index ? "picked" : ""} ${
                    feedback && task.choice === index ? (feedback.passed ? "right" : "wrong") : ""
                  }`}
                  onClick={() => {
                    setTask({ ...task, choice: index, passed: false });
                    setFeedback(null);
                    void save({ choice: index });
                  }}
                >
                  <span className="choice-letter">{String.fromCharCode(65 + index)}</span>
                  <span className="mono">{text}</span>
                </button>
              ))}
            </div>
          )}
        </section>
        {task.kind !== "predict" && (
          <section className="review-editor card">
            <CodeEditor
              fileKey={`${chapter}:${task.index}`}
              value={code}
              label="Review code"
              onChange={(text) => {
                setCode(text);
                setFeedback(null);
                window.clearTimeout(timer.current);
                timer.current = window.setTimeout(() => void save({ code: text }), 400);
              }}
              onRun={() => void check()}
              onCheck={() => void check()}
            />
          </section>
        )}
      </div>
      {aid && (
        <section className="callout aid-callout">
          {aid.kind === "hint" ? <Lightbulb size={16} /> : <Eye size={16} />}
          <div>
            {aid.kind === "hint" ? (
              <p>{aid.text}</p>
            ) : (
              <>
                <p className="muted small">Reference, read only. Your code is unchanged.</p>
                <CodeBlock code={aid.text} />
              </>
            )}
          </div>
        </section>
      )}
      {feedback && (
        <section className={`check-banner ${feedback.passed ? "passed" : "failed"}`}>
          {feedback.passed ? <CircleCheck size={18} /> : <CircleX size={18} />}
          <div>
            <strong>{feedback.passed ? "Passed" : "Not yet"}</strong>
            <span>{feedback.text}</span>
            {feedback.cases.length > 0 && (
              <ul className="mini-cases">
                {feedback.cases.map((item) => (
                  <li key={item.number} className={item.passed ? "ok" : "bad"}>
                    {item.passed ? <CircleCheck size={13} /> : <CircleX size={13} />} {item.label}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      )}
      <footer className="review-actions">
        <button className="btn ghost" onClick={() => navigate("/review")}>
          <ArrowLeft size={15} /> All reviews
        </button>
        <span className="spacer" />
        <button className="btn ghost" onClick={() => void showAid("hint")}>
          <Lightbulb size={15} /> Hint
        </button>
        {task.kind !== "predict" && (
          <button className="btn ghost" onClick={() => void showAid("reference")}>
            <Eye size={15} /> Reference
          </button>
        )}
        <button className="btn" onClick={() => void check()} disabled={checking}>
          {checking ? <Spinner size={14} /> : <CircleCheck size={15} />} Check <Kbd>{mod}↵</Kbd>
        </button>
        <button className="btn primary" disabled={!task.passed} onClick={() => void next()}>
          {task.last ? "Finish" : "Next"} <ArrowRight size={15} />
        </button>
      </footer>
    </div>
  );
}
