import { useMemo, useState } from "react";
import { GitCompareArrows, FileCode2 } from "lucide-react";
import { Dialog } from "../components/ui";
import { CodeBlock } from "../components/Markdown";
import { diffLines } from "./diff";

export function ReferenceDialog({
  files,
  drafts,
  entrypoint,
  onClose,
}: {
  files: Record<string, string>;
  drafts: Record<string, string>;
  entrypoint: string;
  onClose: () => void;
}) {
  const names = Object.keys(files).sort((a, b) =>
    a === entrypoint ? -1 : b === entrypoint ? 1 : a.localeCompare(b),
  );
  const [name, setName] = useState(names[0]);
  const [comparing, setComparing] = useState(false);
  const diff = useMemo(
    () => diffLines(drafts[name] ?? "", files[name] ?? ""),
    [drafts, files, name],
  );
  const identical = diff.every((line) => line.kind === "same");

  return (
    <Dialog
      title="Reference solution"
      onClose={onClose}
      wide
      footer={
        <>
          <p className="muted small">
            Explain one difference: which input exposes it, and why does the result change?
          </p>
          <button className="btn primary" onClick={onClose} data-autofocus>
            Back to my work
          </button>
        </>
      }
    >
      <p className="muted">
        One correct approach. Your draft stays exactly as it is; compare the reasoning rather than
        copying.
      </p>
      <div className="reference-bar">
        <div className="segmented" role="tablist" aria-label="Reference files">
          {names.map((item) => (
            <button
              key={item}
              role="tab"
              aria-selected={item === name}
              className={item === name ? "on" : ""}
              onClick={() => setName(item)}
            >
              <FileCode2 size={13} /> {item}
            </button>
          ))}
        </div>
        <button
          className={`btn sm ${comparing ? "toggled" : ""}`}
          aria-pressed={comparing}
          onClick={() => setComparing(!comparing)}
        >
          <GitCompareArrows size={14} /> Compare with my draft
        </button>
      </div>
      {comparing ? (
        identical ? (
          <p className="callout">
            No textual differences. Explain why your approach meets the requirements.
          </p>
        ) : (
          <figure className="code-block diff">
            <figcaption>
              <span className="remove-key">− your draft</span>
              <span className="add-key">+ reference</span>
            </figcaption>
            <pre>
              <code>
                {diff.map((line, index) => (
                  <div key={index} className={`diff-line ${line.kind}`}>
                    <span className="diff-mark">
                      {line.kind === "add" ? "+" : line.kind === "remove" ? "−" : " "}
                    </span>
                    {line.text || " "}
                  </div>
                ))}
              </code>
            </pre>
          </figure>
        )
      ) : (
        <CodeBlock
          code={files[name]}
          language={name.endsWith(".py") ? "python" : "text"}
          label={name}
        />
      )}
    </Dialog>
  );
}
