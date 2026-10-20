import { useEffect, useRef } from "react";
import {
  autocompletion,
  closeBrackets,
  closeBracketsKeymap,
  completionKeymap,
} from "@codemirror/autocomplete";
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import {
  bracketMatching,
  indentOnInput,
  indentUnit,
  syntaxHighlighting,
} from "@codemirror/language";
import { highlightSelectionMatches, searchKeymap } from "@codemirror/search";
import { Compartment, EditorState, Prec, type Extension } from "@codemirror/state";
import {
  drawSelection,
  dropCursor,
  EditorView,
  highlightActiveLine,
  highlightActiveLineGutter,
  highlightSpecialChars,
  keymap,
  lineNumbers,
  placeholder as placeholderText,
  rectangularSelection,
} from "@codemirror/view";
import { highlighter } from "../highlight";

type Handlers = {
  onChange?: (text: string) => void;
  onRun?: () => void;
  onCheck?: () => void;
  onSave?: () => void;
};

const theme = EditorView.theme({
  "&": {
    height: "100%",
    backgroundColor: "transparent",
    color: "var(--tk-var)",
  },
  ".cm-scroller": { fontFamily: "var(--font-mono)", lineHeight: "1.6" },
  ".cm-content": { padding: "14px 0 40vh", caretColor: "var(--yellow)" },
  ".cm-line": { padding: "0 18px 0 6px" },
  ".cm-gutters": {
    backgroundColor: "transparent",
    color: "var(--text-3)",
    border: "none",
    paddingLeft: "10px",
  },
  ".cm-lineNumbers .cm-gutterElement": { minWidth: "32px", opacity: 0.7 },
  ".cm-activeLineGutter": {
    backgroundColor: "transparent",
    color: "var(--text)",
  },
  ".cm-activeLine": { backgroundColor: "var(--hover)" },
  "&.cm-focused .cm-cursor": {
    borderLeftColor: "var(--yellow)",
    borderLeftWidth: "2px",
  },
  "&.cm-focused .cm-selectionBackground, .cm-selectionBackground, ::selection": {
    backgroundColor: "var(--blue-soft) !important",
  },
  ".cm-selectionMatch": { backgroundColor: "rgba(255, 211, 67, 0.12)" },
  "&.cm-focused .cm-matchingBracket": {
    backgroundColor: "var(--blue-soft)",
    outline: "1px solid var(--blue-line)",
  },
  ".cm-placeholder": { color: "var(--text-3)", fontStyle: "italic" },
  ".cm-tooltip": {
    backgroundColor: "var(--surface-2)",
    border: "1px solid var(--border-strong)",
    borderRadius: "8px",
    boxShadow: "var(--shadow)",
    overflow: "hidden",
  },
  ".cm-tooltip-autocomplete > ul > li": {
    fontFamily: "var(--font-mono)",
    padding: "3px 10px",
  },
  ".cm-tooltip-autocomplete > ul > li[aria-selected]": {
    backgroundColor: "var(--blue-soft)",
    color: "var(--text)",
  },
  ".cm-panels": { backgroundColor: "var(--surface-2)", color: "var(--text)" },
  ".cm-panels.cm-panels-top": { borderBottom: "1px solid var(--border)" },
  ".cm-search input, .cm-search button": {
    fontFamily: "var(--font-ui)",
    fontSize: "12px",
  },
});

function base(handlers: React.RefObject<Handlers>): Extension[] {
  const call = (name: keyof Omit<Handlers, "onChange">) => () => {
    handlers.current?.[name]?.();
    return true;
  };
  return [
    Prec.highest(
      keymap.of([
        { key: "Mod-Enter", run: call("onRun") },
        { key: "Shift-Mod-Enter", run: call("onCheck") },
        { key: "Mod-s", run: call("onSave") },
      ]),
    ),
    lineNumbers(),
    highlightActiveLineGutter(),
    highlightSpecialChars(),
    history(),
    drawSelection(),
    dropCursor(),
    indentOnInput(),
    indentUnit.of("    "),
    EditorState.tabSize.of(4),
    syntaxHighlighting(highlighter),
    bracketMatching(),
    closeBrackets(),
    autocompletion({ activateOnTypingDelay: 250 }),
    rectangularSelection(),
    highlightActiveLine(),
    highlightSelectionMatches(),
    keymap.of([
      ...closeBracketsKeymap,
      ...defaultKeymap,
      ...searchKeymap,
      ...historyKeymap,
      ...completionKeymap,
      indentWithTab,
    ]),
    theme,
    EditorView.updateListener.of((update) => {
      if (update.docChanged) handlers.current?.onChange?.(update.state.doc.toString());
    }),
  ];
}

/**
 * A CodeMirror editor that keeps a separate state per file, so undo history and the cursor
 * survive switching files. A value that differs from the document came from outside.
 */
export function CodeEditor({
  fileKey,
  value,
  language = "python",
  readOnly = false,
  fontSize = 14,
  placeholder,
  label,
  ...handlers
}: Handlers & {
  fileKey: string;
  value: string;
  language?: "python" | "text";
  readOnly?: boolean;
  fontSize?: number;
  placeholder?: string;
  label: string;
}) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const states = useRef(new Map<string, EditorState>());
  const current = useRef(fileKey);
  const handlerRef = useRef<Handlers>(handlers);
  const settings = useRef(new Compartment());
  useEffect(() => {
    handlerRef.current = handlers;
  });

  const configure = (lang: string, locked: boolean, hint?: string, name?: string) => [
    lang === "python" ? python() : [],
    EditorState.readOnly.of(locked),
    EditorView.editable.of(!locked),
    hint ? placeholderText(hint) : [],
    EditorView.contentAttributes.of({ "aria-label": name ?? "Code editor" }),
  ];

  const create = (text: string) =>
    EditorState.create({
      doc: text,
      extensions: [
        base(handlerRef),
        settings.current.of(configure(language, readOnly, placeholder, label)),
      ],
    });

  useEffect(() => {
    const editor = new EditorView({
      state: create(value),
      parent: host.current!,
    });
    view.current = editor;
    return () => {
      editor.destroy();
      view.current = null;
    };
    // The editor is created once; later props are applied by the effects below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const editor = view.current;
    if (!editor) return;
    if (current.current !== fileKey) {
      states.current.set(current.current, editor.state);
      current.current = fileKey;
      const saved = states.current.get(fileKey);
      editor.setState(saved && saved.doc.toString() === value ? saved : create(value));
      return;
    }
    const doc = editor.state.doc.toString();
    if (doc !== value) {
      const head = Math.min(editor.state.selection.main.head, value.length);
      editor.dispatch({
        changes: { from: 0, to: doc.length, insert: value },
        selection: { anchor: head },
      });
    }
    // create() reads the latest props through closures on purpose.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileKey, value]);

  useEffect(() => {
    view.current?.dispatch({
      effects: settings.current.reconfigure(configure(language, readOnly, placeholder, label)),
    });
  }, [language, readOnly, placeholder, label]);

  return <div className="code-editor" ref={host} style={{ fontSize }} />;
}

export function focusEditor(element: HTMLElement | null) {
  element?.querySelector<HTMLElement>(".cm-content")?.focus();
}
