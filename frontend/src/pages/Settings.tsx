import { useMemo, useState } from "react";
import { Check, Copy, Minus, Monitor, Moon, RotateCcw, Sun } from "lucide-react";
import { api } from "../api";
import { useApp } from "../context";
import { TopBarSlot } from "../components/ui";
import { navigate } from "../router";
import type { AppState } from "../types";

export function Topics() {
  const { catalog, state, setState, fail, toast } = useApp();
  const [chosen, setChosen] = useState(() => new Set(state.familiar));
  const changed = useMemo(
    () => chosen.size !== state.familiar.length || state.familiar.some((item) => !chosen.has(item)),
    [chosen, state.familiar],
  );
  const toggle = (concepts: string[], on: boolean) => {
    const next = new Set(chosen);
    for (const concept of concepts) {
      if (on) next.add(concept);
      else next.delete(concept);
    }
    setChosen(next);
  };
  const save = async () => {
    try {
      setState(await api<AppState>("/familiar", { concepts: [...chosen] }));
      toast("Known topics saved. Continue now skips lessons you already know.", "success");
    } catch (error) {
      fail(error);
    }
  };
  return (
    <div className="page topics">
      <TopBarSlot>
        <nav className="crumbs">
          <span className="current">Known topics</span>
        </nav>
        <button className="btn primary sm" disabled={!changed} onClick={() => void save()}>
          <Check size={14} /> Save topics
        </button>
      </TopBarSlot>
      <header className="page-head">
        <div>
          <p className="eyebrow">Skip what you already know</p>
          <h1>Known topics</h1>
          <p className="muted">
            Continue skips a lesson when every one of its topics is checked. Known lessons stay open
            to you in the syllabus, and nothing counts as completed until you pass it.
          </p>
        </div>
      </header>
      <div className="topic-groups">
        {catalog.categories.map((category) => {
          const count = category.concepts.filter((item) => chosen.has(item)).length;
          const all = count === category.concepts.length;
          return (
            <section key={category.id} className="topic-group card">
              <header>
                <button
                  className={`checkbox ${all ? "on" : count ? "some" : ""}`}
                  role="checkbox"
                  aria-checked={all ? true : count ? "mixed" : false}
                  onClick={() => toggle(category.concepts, !all)}
                >
                  {all ? (
                    <Check size={12} strokeWidth={3} />
                  ) : count ? (
                    <Minus size={12} strokeWidth={3} />
                  ) : null}
                </button>
                <h2>{category.title}</h2>
                <span className="muted small">
                  {count}/{category.concepts.length} known
                </span>
              </header>
              <div className="topic-chips">
                {category.concepts.map((concept) => (
                  <button
                    key={concept}
                    className={`topic-chip ${chosen.has(concept) ? "on" : ""}`}
                    aria-pressed={chosen.has(concept)}
                    onClick={() => toggle([concept], !chosen.has(concept))}
                  >
                    {chosen.has(concept) && <Check size={12} strokeWidth={3} />}
                    {concept}
                  </button>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}

export function Settings() {
  const { state, setState, setTheme, confirm, fail, toast, catalog } = useApp();
  const theme = state.settings.theme;
  const restart = async () => {
    const proceed = await confirm({
      title: "Start over?",
      body: "This erases your course progress, drafts, game history, and reviews from this profile. Your workspace folders are moved into the exports folder first, and every terminal closes.",
      confirm: "Erase progress and start over",
      danger: true,
    });
    if (!proceed) return;
    try {
      const result = await api<{ backup: string | null; state: AppState }>("/restart", {});
      setState(result.state);
      toast(
        result.backup
          ? `Progress cleared. Workspaces moved to ${result.backup}`
          : "Progress cleared.",
        "success",
      );
      navigate("/");
    } catch (error) {
      fail(error);
    }
  };
  return (
    <div className="page settings">
      <TopBarSlot>
        <nav className="crumbs">
          <span className="current">Settings</span>
        </nav>
      </TopBarSlot>
      <header className="page-head">
        <div>
          <p className="eyebrow">Pytuitor {catalog.version}</p>
          <h1>Settings</h1>
        </div>
      </header>
      <section className="settings-card card">
        <div className="setting">
          <div>
            <h2>Appearance</h2>
            <p className="muted small">The terminal and editor follow this theme.</p>
          </div>
          <div className="segmented" role="radiogroup" aria-label="Theme">
            {(
              [
                ["dark", "Dark", Moon],
                ["light", "Light", Sun],
                ["system", "System", Monitor],
              ] as const
            ).map(([value, label, Icon]) => (
              <button
                key={value}
                role="radio"
                aria-checked={theme === value}
                className={theme === value ? "on" : ""}
                onClick={() => setTheme(value)}
              >
                <Icon size={14} /> {label}
              </button>
            ))}
          </div>
        </div>
        <div className="setting">
          <div>
            <h2>Your profile</h2>
            <p className="muted small">
              Progress, drafts, workspaces, backups, and exports live here, on this computer only.
            </p>
            <code className="block path">{state.data_dir}</code>
          </div>
          <button
            className="btn sm"
            onClick={() =>
              navigator.clipboard
                .writeText(state.data_dir)
                .then(() => toast("Profile path copied."))
                .catch(() => toast("Select and copy the path instead.", "error"))
            }
          >
            <Copy size={14} /> Copy path
          </button>
        </div>
        <div className="setting">
          <div>
            <h2>Privacy and execution</h2>
            <p className="muted small">
              Lessons, checks, and progress work offline with no account. Your programs run on this
              computer with your user's permissions; process limits are not a security sandbox. The
              embedded terminal is a real shell, so commands you type there behave as they would in
              any terminal.
            </p>
          </div>
        </div>
      </section>
      <section className="settings-card card danger-zone">
        <div className="setting">
          <div>
            <h2>Start over</h2>
            <p className="muted small">
              Erase this profile's progress and return to the welcome screen. Workspace folders are
              kept as a backup.
            </p>
          </div>
          <button className="btn danger" onClick={() => void restart()}>
            <RotateCcw size={14} /> Start over…
          </button>
        </div>
      </section>
    </div>
  );
}
