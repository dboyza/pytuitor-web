import { useState, type FormEvent } from "react";
import {
  CircleCheck,
  FilePlus2,
  PanelLeftClose,
  PanelLeftOpen,
  Play,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import { CodeEditor } from "../components/CodeEditor";
import { Kbd, Spinner } from "../components/ui";
import { mod } from "../context";
import type { Stage } from "../types";
import type { Workspace } from "./useWorkspace";

// Nerd Font file glyphs, rendered with the bundled JetBrains Mono Nerd Font.
const GLYPHS: Record<string, [string, string]> = {
  py: ["", "py"],
  json: ["", "json"],
  md: ["", "md"],
  csv: ["", "csv"],
  txt: ["", "txt"],
  toml: ["", "toml"],
  cfg: ["", "cfg"],
  ini: ["", "cfg"],
};

export function FileGlyph({ name }: { name: string }) {
  const extension = name.split(".").pop()?.toLowerCase() ?? "";
  const [glyph, kind] = GLYPHS[extension] ?? ["", "file"];
  return (
    <span className={`glyph ${kind}`} aria-hidden="true">
      {glyph}
    </span>
  );
}

function SaveState({ status }: { status: Workspace["status"] }) {
  return (
    <span className={`save-state ${status}`} role="status" aria-live="polite">
      <span className="dot" aria-hidden="true" />
      {status === "saving" ? "Saving" : status === "error" ? "Not saved" : "Saved"}
    </span>
  );
}

export function EditorPane({
  workspace,
  stage,
  checking,
  fontSize,
  onRun,
  onCheck,
  onAdd,
  onRemove,
  onTrack,
}: {
  workspace: Workspace;
  stage: Stage;
  checking: boolean;
  fontSize: number;
  onRun: () => void;
  onCheck: () => void;
  onAdd: (name: string) => Promise<boolean>;
  onRemove: (name: string) => void;
  onTrack: (name: string) => void;
}) {
  const { order, contents, required, untracked, active, preview } = workspace;
  const crowded = order.length > 1 || untracked.length > 0;
  const [explorer, setExplorer] = useState<boolean | null>(null);
  const showExplorer = explorer ?? crowded;
  const [adding, setAdding] = useState(false);
  const [name, setName] = useState("");
  const entry = stage.entrypoint;
  const shown = preview?.name ?? active;
  const isRequired = required.has(active);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return setAdding(false);
    if (await onAdd(name.trim())) {
      setName("");
      setAdding(false);
    }
  };

  return (
    <section className={`editor-pane ${showExplorer ? "with-explorer" : ""}`} aria-label="Editor">
      {showExplorer && (
        <nav className="explorer" aria-label="Workspace files">
          <header>
            <span className="eyebrow">Workspace</span>
            <button
              className="icon-btn"
              aria-label="New file"
              title="New file"
              onClick={() => setAdding(true)}
            >
              <FilePlus2 size={14} />
            </button>
          </header>
          {adding && (
            <form className="new-file" onSubmit={submit}>
              <input
                autoFocus
                value={name}
                placeholder="helpers.py"
                aria-label="New file name"
                spellCheck={false}
                onChange={(event) => setName(event.target.value)}
                onKeyDown={(event) => event.key === "Escape" && setAdding(false)}
                onBlur={() => !name && setAdding(false)}
              />
            </form>
          )}
          <ul>
            {order.map((file) => (
              <li key={file} className="file-row">
                <button
                  className={`file ${file === active && !preview ? "active" : ""}`}
                  onClick={() => workspace.select(file)}
                  title={file}
                >
                  <FileGlyph name={file} />
                  <span className="file-name">{file}</span>
                  {file === entry ? (
                    <Play size={11} className="file-run" aria-label="Run starts here" />
                  ) : (
                    required.has(file) && (
                      <span className="file-required" title="Required file" aria-label="Required">
                        •
                      </span>
                    )
                  )}
                </button>
                {!required.has(file) && (
                  <button
                    className="file-action"
                    aria-label={`Remove ${file}`}
                    title="Remove (backs up the workspace first)"
                    onClick={() => onRemove(file)}
                  >
                    <Trash2 size={12} />
                  </button>
                )}
              </li>
            ))}
          </ul>
          {untracked.length > 0 && (
            <>
              <header className="sub">
                <span className="eyebrow">Other files</span>
              </header>
              <p className="explorer-note">Created in the terminal. Not included in checks.</p>
              <ul>
                {untracked.map((file) => (
                  <li key={file.name} className="file-row">
                    <button
                      className={`file untracked ${preview?.name === file.name ? "active" : ""}`}
                      onClick={() => void workspace.showPreview(file.name)}
                      title={`${file.name} · ${file.size} bytes`}
                    >
                      <FileGlyph name={file.name} />
                      <span className="file-name">{file.name}</span>
                    </button>
                    <button
                      className="file-action"
                      aria-label={`Add ${file.name} to the workspace`}
                      title="Add to workspace"
                      onClick={() => onTrack(file.name)}
                    >
                      <Plus size={12} />
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
          <footer className="legend">
            <span>
              <Play size={10} /> Run file
            </span>
            <span>
              <span className="file-required">•</span> Required
            </span>
          </footer>
        </nav>
      )}
      <div className="editor-main">
        <header className="editor-bar">
          <button
            className="icon-btn"
            aria-label={showExplorer ? "Hide files" : "Show files"}
            aria-pressed={showExplorer}
            title={showExplorer ? "Hide files" : "Show files"}
            onClick={() => setExplorer(!showExplorer)}
          >
            {showExplorer ? <PanelLeftClose size={15} /> : <PanelLeftOpen size={15} />}
          </button>
          <div className="editor-file">
            <FileGlyph name={shown} />
            <span className="mono">{shown}</span>
            {preview ? (
              <span className="badge muted">Preview · not in checks</span>
            ) : active === entry ? (
              <span className="badge blue" title="Run and Check start here">
                <Play size={10} /> Run file
              </span>
            ) : (
              <span className="badge">{isRequired ? "Required" : "Extra file"}</span>
            )}
          </div>
          <div className="editor-actions">
            <SaveState status={workspace.status} />
            <button
              className="btn sm"
              onClick={onRun}
              title={`Run ${stage.run} in the terminal (${mod}↵)`}
            >
              <Play size={14} /> Run
            </button>
            <button
              className="btn primary sm"
              onClick={onCheck}
              disabled={checking}
              title={`Check your work (${mod}⇧↵)`}
            >
              {checking ? <Spinner size={13} /> : <CircleCheck size={14} />} Check
            </button>
          </div>
        </header>
        {preview && (
          <div className="preview-banner">
            <span>
              This file was created outside the editor. Add it to the workspace to edit it and
              include it in checks.
            </span>
            <button className="btn sm" onClick={() => onTrack(preview.name)}>
              <Plus size={13} /> Add to workspace
            </button>
            <button
              className="icon-btn"
              aria-label="Close preview"
              onClick={workspace.closePreview}
            >
              <X size={14} />
            </button>
          </div>
        )}
        <div className="editor-host">
          {shown && (
            <CodeEditor
              fileKey={preview ? `preview:${preview.name}` : active}
              value={preview ? preview.content : (contents[active] ?? "")}
              language={shown.endsWith(".py") ? "python" : "text"}
              readOnly={!!preview}
              fontSize={fontSize}
              label={`Editor: ${shown}`}
              placeholder={
                stage.stage === "build" && active === entry
                  ? `# Write your program here, then press ${mod}↵ to run it in the terminal.`
                  : undefined
              }
              onChange={(text) => !preview && workspace.edit(active, text)}
              onRun={onRun}
              onCheck={onCheck}
              onSave={() => void workspace.flush()}
            />
          )}
        </div>
        <footer className="editor-foot">
          <span>
            <Kbd>{mod}↵</Kbd> Run
          </span>
          <span>
            <Kbd>{mod}⇧↵</Kbd> Check
          </span>
          <span>
            <Kbd>Ctrl `</Kbd> Terminal
          </span>
          <span className="spacer" />
          <span className="muted">Python · UTF-8 · 4 spaces</span>
        </footer>
      </div>
    </section>
  );
}
