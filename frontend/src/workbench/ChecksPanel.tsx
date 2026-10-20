import { useState } from "react";
import {
  ArrowRight,
  ChevronRight,
  CircleCheck,
  CircleX,
  FlaskConical,
  Lightbulb,
  PartyPopper,
  TriangleAlert,
} from "lucide-react";
import type { CheckCase, CheckOutcome } from "../types";
import { Kbd, Spinner } from "../components/ui";
import { mod } from "../context";

export type CheckRun = {
  running: boolean;
  cases: Record<number, CheckCase>;
  outcome: CheckOutcome | null;
  failure: string;
  stale: boolean;
};

export const idleRun: CheckRun = {
  running: false,
  cases: {},
  outcome: null,
  failure: "",
  stale: false,
};

function show(value: string | undefined) {
  if (value === undefined || value === "") return <span className="muted">nothing</span>;
  return value;
}

function CaseRow({
  item,
  open,
  onToggle,
}: {
  item: CheckCase;
  open: boolean;
  onToggle: () => void;
}) {
  const running = item.status === "running";
  const failed = item.passed === false;
  const evidence = item.observations?.find((observation) => !observation.passed);
  return (
    <li
      className={`case ${running ? "running" : failed ? "failed" : "passed"} ${open ? "open" : ""}`}
    >
      <button className="case-head" aria-expanded={open} onClick={onToggle}>
        <span className="case-icon">
          {running ? (
            <Spinner size={15} />
          ) : failed ? (
            <CircleX size={17} />
          ) : (
            <CircleCheck size={17} />
          )}
        </span>
        <span className="case-number">{item.number}</span>
        <span className="case-label">{item.label}</span>
        <ChevronRight size={15} className="chevron" />
      </button>
      {open && !running && (
        <div className="case-body">
          <dl className="evidence">
            <dt>Test</dt>
            <dd>
              <code className="block">{item.operation}</code>
            </dd>
            {evidence ? (
              <>
                <dt>Looked at</dt>
                <dd>{evidence.label}</dd>
                <dt>Expected</dt>
                <dd>
                  <code className="block">
                    {evidence.comparison} {evidence.expected}
                  </code>
                </dd>
                <dt>Actual</dt>
                <dd>
                  <code className={`block ${failed ? "bad" : ""}`}>{evidence.actual}</code>
                </dd>
              </>
            ) : (
              <>
                <dt>Expected</dt>
                <dd>
                  <code className="block">{show(item.expected)}</code>
                </dd>
                <dt>Actual</dt>
                <dd>
                  <code className={`block ${failed ? "bad" : ""}`}>{show(item.actual)}</code>
                </dd>
              </>
            )}
            {item.input.trim() && (
              <>
                <dt>Typed input</dt>
                <dd>
                  <code className="block">{item.input.replace(/\n$/, "")}</code>
                </dd>
              </>
            )}
            {item.expected_output !== null && (
              <>
                <dt>Expected output</dt>
                <dd>
                  <code className="block">{show(item.expected_output)}</code>
                </dd>
              </>
            )}
            <dt>Printed output</dt>
            <dd>
              <code className="block">{show(item.output)}</code>
            </dd>
          </dl>
          {(item.observations?.length ?? 0) > 1 && (
            <ul className="observations">
              {item.observations!.map((observation, index) => (
                <li key={index} className={observation.passed ? "ok" : "bad"}>
                  {observation.passed ? <CircleCheck size={13} /> : <CircleX size={13} />}
                  <span>{observation.label}</span>
                  <code>
                    {observation.actual} {observation.comparison} {observation.expected}
                  </code>
                </li>
              ))}
            </ul>
          )}
          {failed && (
            <p className="nudge">
              <Lightbulb size={15} />
              <span>{item.nudge}</span>
            </p>
          )}
        </div>
      )}
    </li>
  );
}

export function ChecksPanel({
  run,
  total,
  label,
  onCheck,
  onAdvance,
  advanceLabel,
}: {
  run: CheckRun;
  total: number;
  label: string;
  onCheck: () => void;
  onAdvance?: () => void;
  advanceLabel?: string;
}) {
  const cases = Object.values(run.cases).sort((a, b) => a.number - b.number);
  const firstFailure = cases.find((item) => item.passed === false)?.number;
  const [chosen, setChosen] = useState<Set<number> | null>(null);
  const openSet = chosen ?? new Set(firstFailure ? [firstFailure] : []);
  const toggle = (number: number) => {
    const next = new Set(openSet);
    if (next.has(number)) next.delete(number);
    else next.add(number);
    setChosen(next);
  };
  const finished = cases.filter((item) => item.status === "finished");
  const passed = finished.filter((item) => item.passed).length;
  const outcome = run.outcome;

  if (!cases.length && !run.running && !run.failure && !outcome) {
    return (
      <div className="checks-empty">
        <div className="empty-art">
          <FlaskConical size={30} strokeWidth={1.5} />
        </div>
        <h3>No checks yet</h3>
        <p>
          Check runs {total} automated {total === 1 ? "test" : "tests"} against a clean copy of your
          workspace and shows exactly what each one expected.
        </p>
        <button className="btn primary" onClick={onCheck}>
          <CircleCheck size={16} /> Check {label}
          <Kbd>{mod}⇧↵</Kbd>
        </button>
      </div>
    );
  }

  return (
    <div className="checks">
      {run.running && (
        <div className="check-banner running">
          <Spinner size={16} />
          <div>
            <strong>
              Checking {Math.min(finished.length + 1, total)} of {total}
            </strong>
            <span>Each test runs your program in a fresh folder.</span>
          </div>
          <div className="meter">
            <span
              style={{
                width: `${(finished.length / Math.max(total, 1)) * 100}%`,
              }}
            />
          </div>
        </div>
      )}
      {!run.running && run.failure && (
        <div className="check-banner failed">
          <TriangleAlert size={18} />
          <div>
            <strong>The check could not finish</strong>
            <span>{run.failure}</span>
          </div>
        </div>
      )}
      {!run.running && outcome && outcome.passed && (
        <div className="check-banner passed celebrate">
          <PartyPopper size={20} />
          <div>
            <strong>
              {outcome.flags.completed ? "Lesson complete!" : `${label} passed`} · {passed}/{total}{" "}
              checks
            </strong>
            <span>{outcome.summary}</span>
          </div>
          {onAdvance && (
            <button className="btn primary sm" onClick={onAdvance}>
              {advanceLabel} <ArrowRight size={14} />
            </button>
          )}
        </div>
      )}
      {!run.running && outcome && !outcome.passed && (
        <div className="check-banner failed">
          {outcome.error ? <TriangleAlert size={18} /> : <CircleX size={18} />}
          <div>
            <strong>
              {outcome.error
                ? "Your program stopped with an error"
                : `${passed} of ${total} checks passed`}
            </strong>
            {outcome.error && <code className="block bad">{outcome.error}</code>}
            <span>
              {outcome.error
                ? outcome.guidance || "Read the error, edit, and Check again."
                : "Compare what each check expected with what your program did, then edit and Check again."}
            </span>
          </div>
        </div>
      )}
      {!run.running && !outcome && !run.failure && cases.length > 0 && (
        <div
          className={`check-banner ${run.stale ? "stale" : passed === total ? "passed" : "failed"}`}
        >
          {passed === total ? <CircleCheck size={18} /> : <CircleX size={18} />}
          <div>
            <strong>
              Last check · {passed} of {total} passed
            </strong>
            <span>
              {run.stale
                ? "Your draft changed since this check. Check again to verify your current work."
                : "These results match your current draft."}
            </span>
          </div>
        </div>
      )}
      <ol className="cases">
        {cases.map((item) => (
          <CaseRow
            key={item.number}
            item={item}
            open={openSet.has(item.number)}
            onToggle={() => toggle(item.number)}
          />
        ))}
      </ol>
    </div>
  );
}
