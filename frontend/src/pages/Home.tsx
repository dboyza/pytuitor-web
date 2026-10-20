import { useMemo, useState } from "react";
import { ArrowRight, Compass, ListTree, NotebookPen, Repeat2, Sparkles } from "lucide-react";
import { useApp } from "../context";
import { ProgressRing, StatusIcon, TopBarSlot } from "../components/ui";
import { learnPath, navigate } from "../router";
import type { Chapter } from "../types";

function greeting() {
  const hour = new Date().getHours();
  return hour < 5
    ? "Working late"
    : hour < 12
      ? "Good morning"
      : hour < 18
        ? "Good afternoon"
        : "Good evening";
}

export function ChapterLessons({ chapter }: { chapter: Chapter }) {
  const { catalog, state } = useApp();
  return (
    <ol className="lesson-list">
      {chapter.activities.map((id, index) => {
        const item = catalog.activities[id];
        const status = state.statuses[id];
        const current = state.last_lesson === id;
        return (
          <li key={id}>
            <a
              href={learnPath(id)}
              className={`lesson-row ${current ? "current" : ""}`}
              onClick={(event) => {
                event.preventDefault();
                navigate(learnPath(id));
              }}
            >
              <StatusIcon status={status} />
              <span className="lesson-index">{String(index + 1).padStart(2, "0")}</span>
              <span className="lesson-text">
                <span className="lesson-title">
                  {item.title}
                  {item.milestone && (
                    <span className="badge yellow">
                      <Compass size={11} /> Game
                    </span>
                  )}
                  {status === "familiar" && <span className="badge">Known</span>}
                </span>
                <span className="lesson-sub">{item.subtitle}</span>
              </span>
              <span className="lesson-minutes">{item.minutes} min</span>
              <ArrowRight size={15} className="lesson-go" />
            </a>
          </li>
        );
      })}
    </ol>
  );
}

export function Home() {
  const { catalog, state } = useApp();
  const next = state.next ? catalog.activities[state.next.id] : null;
  const nextChapter = next ? catalog.chapters.find((c) => c.id === next.chapter_id) : null;
  const initial =
    (state.last_lesson && catalog.activities[state.last_lesson]?.chapter_id) ||
    next?.chapter_id ||
    catalog.chapters[0].id;
  const [chapterId, setChapterId] = useState(initial);
  const chapter = catalog.chapters.find((c) => c.id === chapterId)!;
  const sections = useMemo(
    () =>
      catalog.sections.map((section) => ({
        section,
        chapters: catalog.chapters.filter((c) => c.section_id === section.id),
      })),
    [catalog],
  );
  const chapterDone = (c: Chapter) =>
    c.activities.filter((id) => ["completed", "familiar"].includes(state.statuses[id])).length;
  const { core, optional } = state.progress;
  const milestones = Object.values(catalog.activities).filter((a) => a.milestone);
  const gameDone = milestones.filter((a) => state.statuses[a.id] === "completed").length;
  const review = state.review_suggested
    ? catalog.chapters.find((c) => c.id === state.review_suggested)
    : null;

  return (
    <div className="page home">
      <TopBarSlot>
        <nav className="crumbs">
          <span className="current">Home</span>
        </nav>
      </TopBarSlot>
      <header className="page-head">
        <div>
          <p className="eyebrow">{greeting()}</p>
          <h1>Your Python path</h1>
        </div>
      </header>

      <div className="home-grid">
        <section className="continue-card">
          <div className="continue-art" aria-hidden="true" />
          {next && nextChapter ? (
            <>
              <p className="eyebrow">
                Up next · Chapter {nextChapter.number} · {nextChapter.title}
              </p>
              <h2>{next.title}</h2>
              <p className="muted">{next.subtitle}</p>
              <p className="continue-summary">
                <StatusIcon status={state.next!.status} size={16} /> {state.next!.summary}
              </p>
              {state.next!.note && (
                <p className="continue-note">
                  <NotebookPen size={14} /> {state.next!.note}
                </p>
              )}
              <div className="row">
                <button className="btn primary lg" onClick={() => navigate(learnPath(next.id))}>
                  Continue <ArrowRight size={17} />
                </button>
                <span className="muted small">
                  {next.milestone ? "Game milestone" : "Lesson"} · {next.minutes} min
                </span>
              </div>
            </>
          ) : (
            <>
              <p className="eyebrow">Choose your next chapter</p>
              <h2>You've finished this path</h2>
              <p className="muted">Open the syllabus to explore optional depth and specialties.</p>
              <button className="btn primary lg" onClick={() => navigate("/syllabus")}>
                <ListTree size={17} /> Open syllabus
              </button>
            </>
          )}
        </section>

        <section className="stat-card">
          <ProgressRing value={core.completed + core.familiar} total={core.total} size={76}>
            <strong>
              {Math.round(((core.completed + core.familiar) / Math.max(1, core.total)) * 100)}%
            </strong>
          </ProgressRing>
          <div>
            <p className="eyebrow">Core course</p>
            <p className="stat-number">
              {core.completed}
              <span>/{core.total}</span>
            </p>
            <p className="muted small">
              completed{core.familiar ? ` · ${core.familiar} known` : ""}
            </p>
          </div>
        </section>

        <section className="stat-card">
          <ProgressRing value={optional.completed} total={optional.total} size={76} tone="yellow">
            <strong>{optional.completed}</strong>
          </ProgressRing>
          <div>
            <p className="eyebrow">Optional depth</p>
            <p className="stat-number">
              {optional.completed}
              <span>/{optional.total}</span>
            </p>
            <p className="muted small">Python depth, specialties, and the web</p>
          </div>
        </section>

        <button className="stat-card link" onClick={() => navigate("/game")}>
          <div className="stat-icon yellow">
            <Compass size={22} />
          </div>
          <div>
            <p className="eyebrow">Lantern Reach</p>
            <p className="stat-number">
              {gameDone}
              <span>/{milestones.length}</span>
            </p>
            <p className="muted small">milestones in your game</p>
          </div>
          <ArrowRight size={16} className="stat-go" />
        </button>

        <button
          className={`stat-card link ${review ? "suggested" : ""}`}
          onClick={() => navigate(review ? `/review/${review.id}` : "/review")}
        >
          <div className="stat-icon blue">
            {review ? <Sparkles size={22} /> : <Repeat2 size={22} />}
          </div>
          <div>
            <p className="eyebrow">{review ? "Review suggested" : "Optional review"}</p>
            <p className="stat-title">{review ? review.title : "Mixed practice"}</p>
            <p className="muted small">Predict, repair, and write · 6 to 10 min</p>
          </div>
          <ArrowRight size={16} className="stat-go" />
        </button>
      </div>

      <section className="browser">
        <aside className="chapter-nav" aria-label="Chapters">
          {sections.map(({ section, chapters }) => (
            <div key={section.id} className="chapter-group">
              <p className="eyebrow">
                {section.title}
                {section.optional && <span className="badge">Optional</span>}
              </p>
              {chapters.map((c) => {
                const done = chapterDone(c);
                return (
                  <button
                    key={c.id}
                    className={`chapter-link ${c.id === chapterId ? "on" : ""}`}
                    aria-current={c.id === chapterId}
                    onClick={() => setChapterId(c.id)}
                  >
                    <span className="chapter-number">{c.number}</span>
                    <span className="chapter-name">{c.title}</span>
                    <span
                      className="chapter-progress"
                      title={`${done} of ${c.activities.length} done`}
                    >
                      <span
                        style={{
                          width: `${(done / c.activities.length) * 100}%`,
                        }}
                      />
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </aside>
        <div className="chapter-detail">
          <header>
            <p className="eyebrow">
              Chapter {chapter.number} ·{" "}
              {catalog.sections.find((s) => s.id === chapter.section_id)?.title}
            </p>
            <h2>{chapter.title}</h2>
            <p className="muted">{chapter.outcome}</p>
          </header>
          <ChapterLessons chapter={chapter} />
        </div>
      </section>
    </div>
  );
}
