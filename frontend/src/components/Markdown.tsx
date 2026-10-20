import { memo } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { highlightPython } from "../highlight";

export function CodeBlock({
  code,
  language = "python",
  label,
}: {
  code: string;
  language?: string;
  label?: string;
}) {
  const python = language === "python" || language === "py";
  const text = code.replace(/\n$/, "");
  return (
    <figure className="code-block">
      {(label || python) && <figcaption>{label ?? "Python"}</figcaption>}
      <pre>
        <code>
          {python
            ? highlightPython(text).map((span, index) =>
                span.className ? (
                  <span key={index} className={span.className}>
                    {span.text}
                  </span>
                ) : (
                  span.text
                ),
              )
            : text}
        </code>
      </pre>
    </figure>
  );
}

const components: Components = {
  pre: ({ children }) => <>{children}</>,
  code: ({ className, children }) => {
    const language = /language-([\w-]+)/.exec(className ?? "")?.[1];
    const text = String(children);
    if (!language && !text.includes("\n")) return <code className="inline">{children}</code>;
    return <CodeBlock code={text} language={language ?? "text"} />;
  },
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noreferrer noopener">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="table-wrap">
      <table>{children}</table>
    </div>
  ),
};

export const Markdown = memo(function Markdown({
  text,
  className = "",
}: {
  text: string;
  className?: string;
}) {
  return (
    <div className={`prose ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {text}
      </ReactMarkdown>
    </div>
  );
});
