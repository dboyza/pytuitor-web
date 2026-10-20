import { useState } from "react";
import { ChevronDown, Compass, Search } from "lucide-react";
import { useApp } from "../context";
import { TopBarSlot } from "../components/ui";
import { ChapterLessons } from "./Home";

export function Syllabus() {
  const { catalog, state } = useApp();
  const current = state.last_lesson ? catalog.activities[state.last_lesson]?.chapter_id : null;
  const [open, setOpen] = useState<Set<string>>(new Set(current ? [current] : []));
  const [query, setQuery] = useState("");
  const needle = query.trim().toLowerCase();
  const matches = (chapterId: string) => {
    if (!needle) return true;
    const chapter = catalog.chapters.find((c) => c.id === chapterId)!;
    return [chapter.title, chapter.outcome]
      .concat(
        chapter.activities.flatMap((id) => [
          catalog.activities[id].title,
          catalog.activities[id].subtitle,
          ...catalog.activities[id].concepts,
        ]),
      )
      .some((text) => text.toLowerCase().includes(needle));
  };
  const toggle = (id: string) => {
    const next = new Set(open);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setOpen(next);
  };

  return (
    <div className="page syllabus">
      <TopBarSlot>
        <nav className="crumbs">
          <span className="current">Syllabus</span>
        </nav>
      </TopBarSlot>
      <header className="page-head">
        <div>
          <p className="eyebrow">Curriculum</p>
          <h1>Syllabus</h1>
          <p className="muted">
            {catalog.counts.chapters} chapters · {catalog.counts.lessons} lessons ·{" "}
            {catalog.counts.milestones} game milestones. Lessons are Build then Repair; each game
            milestone is Extend then Repair. Prerequisites are advice, never locks.
          </p>
        </div>
        <label className="search-field">
          <Search size={15} />
          <input
            value={query}
            placeholder="Filter by topic, like dictionaries or async"
            onChange={(event) => setQuery(event.target.value)}
            aria-label="Filter chapters"
          />
        </label>
      </header>

      {catalog.sections.map((section) => {
        const chapters = catalog.chapters.filter(
          (c) => c.section_id === section.id && matches(c.id),
        );
        if (!chapters.length) return null;
        return (
          <section key={section.id} className="syllabus-section">
            <header>
              <h2>
                {section.title}
                {section.optional && <span className="badge">Optional</span>}
              </h2>
              <p className="muted">{section.description}</p>
            </header>
            <div className="chapter-cards">
              {chapters.map((chapter) => {
                const expanded = open.has(chapter.id) || !!needle;
                const done = chapter.activities.filter((id) =>
                  ["completed", "familiar"].includes(state.statuses[id]),
                ).length;
                const lessons = chapter.activities.filter(
                  (id) => !catalog.activities[id].milestone,
                ).length;
                const prerequisites = chapter.prerequisites
                  .map((id) => catalog.chapters.find((c) => c.id === id)?.title)
                  .filter(Boolean);
                return (
                  <article key={chapter.id} className={`chapter-card ${expanded ? "open" : ""}`}>
                    <button
                      className="chapter-card-head"
                      aria-expanded={expanded}
                      onClick={() => toggle(chapter.id)}
                    >
                      <span className="chapter-badge">{chapter.number}</span>
                      <span className="chapter-card-text">
                        <strong>{chapter.title}</strong>
                        <span className="muted">{chapter.outcome}</span>
                        <span className="chapter-card-meta">
                          {lessons} lessons
                          <span className="meta-dot" />
                          <Compass size={12} /> game milestone
                          {prerequisites.length > 0 && (
                            <>
                              <span className="meta-dot" />
                              Builds on {prerequisites.join(", ")}
                            </>
                          )}
                        </span>
                      </span>
                      <span className="chapter-card-progress">
                        {done}/{chapter.activities.length}
                      </span>
                      <ChevronDown size={17} className="chevron" />
                    </button>
                    {expanded && <ChapterLessons chapter={chapter} />}
                  </article>
                );
              })}
            </div>
          </section>
        );
      })}
    </div>
  );
}
