import { useState } from "react";
import {
  ArrowRight,
  BookOpen,
  Compass,
  FlaskConical,
  ListTree,
  SquareTerminal,
  Wrench,
} from "lucide-react";
import { api } from "../api";
import { Logo } from "../components/ui";
import { useApp } from "../context";
import { learnPath, navigate } from "../router";
import type { AppState } from "../types";

const PY = "";
const FOLDER = "";

export function Welcome() {
  const { catalog, setState, fail } = useApp();
  const [busy, setBusy] = useState(false);
  const start = async (browse: boolean) => {
    setBusy(true);
    try {
      const state = await api<AppState>("/onboard", {});
      setState(state);
      if (browse || !state.next) navigate("/syllabus");
      else navigate(learnPath(state.next.id));
    } catch (error) {
      fail(error);
      setBusy(false);
    }
  };
  return (
    <div className="welcome">
      <div className="welcome-glow" aria-hidden="true" />
      <section className="welcome-hero">
        <div className="welcome-brand">
          <Logo size={44} />
          <span>Pytuitor</span>
        </div>
        <h1>
          Learn Python by <span className="gradient-text">building it</span> and{" "}
          <span className="gradient-text alt">fixing it</span>.
        </h1>
        <p className="lede">
          Short lessons beside a real terminal on your computer. Write each program from scratch,
          repair a broken one, and grow your own text adventure along the way.
        </p>
        <div className="row">
          <button className="btn primary lg" disabled={busy} onClick={() => void start(false)}>
            Start learning <ArrowRight size={17} />
          </button>
          <button className="btn lg" disabled={busy} onClick={() => void start(true)}>
            <ListTree size={17} /> Browse syllabus
          </button>
        </div>
        <p className="welcome-meta">
          <strong>{catalog.counts.lessons}</strong> lessons ·{" "}
          <strong>{catalog.counts.milestones}</strong> game milestones ·{" "}
          <strong>{catalog.counts.chapters}</strong> chapters · works offline · no account
        </p>
      </section>

      <section className="welcome-preview" aria-hidden="true">
        <div className="mock">
          <div className="mock-bar">
            <span />
            <span />
            <span />
            <em>First light · Build</em>
          </div>
          <div className="mock-body">
            <div className="mock-lesson">
              <div className="mock-eyebrow">Chapter 1 · First programs</div>
              <div className="mock-title">First light</div>
              <div className="mock-line w90" />
              <div className="mock-line w75" />
              <div className="mock-line w85" />
              <div className="mock-code">
                <span className="tk-call">print</span>(
                <span className="tk-string">"Hello, world!"</span>)
              </div>
              <div className="mock-line w60" />
              <div className="mock-check">
                <span className="ok">✓</span> Prints the greeting
              </div>
              <div className="mock-check">
                <span className="ok">✓</span> Reads a name with input()
              </div>
            </div>
            <div className="mock-right">
              <div className="mock-editor">
                <div>
                  <span className="ln">1</span>
                  <span className="tk-var">name</span> <span className="tk-op">=</span>{" "}
                  <span className="tk-call">input</span>(
                  <span className="tk-string">"Your name? "</span>)
                </div>
                <div>
                  <span className="ln">2</span>
                  <span className="tk-call">print</span>(
                  <span className="tk-string">f"Hello, </span>
                  {"{"}
                  <span className="tk-var">name</span>
                  {"}"}
                  <span className="tk-string">!"</span>)
                </div>
                <div>
                  <span className="ln">3</span>
                  <span className="caret" />
                </div>
              </div>
              <div className="mock-terminal">
                <div>
                  <span className="t-blue">{PY}</span> <span className="t-yellow">first-light</span>{" "}
                  <span className="t-cyan">{FOLDER} build</span> <span className="t-green">❯</span>{" "}
                  python lesson.py
                </div>
                <div>Your name? Ada</div>
                <div>Hello, Ada!</div>
                <div>
                  <span className="t-blue">{PY}</span> <span className="t-yellow">first-light</span>{" "}
                  <span className="t-cyan">{FOLDER} build</span> <span className="t-green">❯</span>{" "}
                  <span className="caret" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="welcome-features">
        <div>
          <BookOpen size={18} />
          <h3>Read a short lesson</h3>
          <p>Plain English, one idea at a time, with worked examples you can try.</p>
        </div>
        <div>
          <SquareTerminal size={18} />
          <h3>Run it for real</h3>
          <p>A real shell sits beside every lesson, in a folder that holds your files.</p>
        </div>
        <div>
          <FlaskConical size={18} />
          <h3>Check, then repair</h3>
          <p>Automated checks show exactly what passed. Then fix a program with a real bug.</p>
        </div>
        <div>
          <Compass size={18} />
          <h3>Grow your own game</h3>
          <p>Every chapter extends Lantern Reach, a text adventure that runs without the tutor.</p>
        </div>
        <div>
          <Wrench size={18} />
          <h3>Go deeper when ready</h3>
          <p>Optional chapters cover Python's machinery, async work, packaging, and the web.</p>
        </div>
      </section>
    </div>
  );
}
