import { highlightTree, tagHighlighter, tags as t } from "@lezer/highlight";
import { parser } from "@lezer/python";

// One highlighter for the editor, lesson examples, and references, styled by --tk-* tokens.
export const highlighter = tagHighlighter([
  {
    tag: [
      t.keyword,
      t.controlKeyword,
      t.definitionKeyword,
      t.moduleKeyword,
      t.operatorKeyword,
      t.modifier,
    ],
    class: "tk-keyword",
  },
  { tag: [t.bool, t.null, t.atom], class: "tk-atom" },
  { tag: t.number, class: "tk-number" },
  { tag: [t.string, t.special(t.string)], class: "tk-string" },
  { tag: [t.escape, t.regexp], class: "tk-escape" },
  { tag: t.function(t.definition(t.variableName)), class: "tk-def" },
  {
    tag: [t.function(t.variableName), t.function(t.propertyName)],
    class: "tk-call",
  },
  { tag: [t.definition(t.className), t.className], class: "tk-class" },
  { tag: t.comment, class: "tk-comment" },
  { tag: t.propertyName, class: "tk-prop" },
  {
    tag: [
      t.arithmeticOperator,
      t.compareOperator,
      t.definitionOperator,
      t.updateOperator,
      t.bitwiseOperator,
    ],
    class: "tk-op",
  },
  { tag: t.meta, class: "tk-meta" },
  { tag: t.variableName, class: "tk-var" },
]);

export type Span = { text: string; className: string };

/** Split Python source into highlighted spans for static rendering. */
export function highlightPython(code: string): Span[] {
  const spans: Span[] = [];
  let position = 0;
  const push = (to: number, className: string) => {
    if (to > position) spans.push({ text: code.slice(position, to), className });
    position = to;
  };
  highlightTree(parser.parse(code), highlighter, (from, to, classes) => {
    push(from, "");
    push(to, classes);
  });
  push(code.length, "");
  return spans;
}
