import { describe, expect, it } from "vitest";
import { diffLines } from "./workbench/diff";
import { highlightPython } from "./highlight";
import { parse } from "./router";

describe("diffLines", () => {
  it("marks only the changed line", () => {
    expect(diffLines('print("a")\nprint(b)\n', 'print("a")\nprint("b")\n')).toEqual([
      { kind: "same", text: 'print("a")' },
      { kind: "remove", text: "print(b)" },
      { kind: "add", text: 'print("b")' },
    ]);
  });

  it("treats an empty draft as no lines", () => {
    expect(diffLines("", "x = 1\n")).toEqual([{ kind: "add", text: "x = 1" }]);
  });
});

describe("highlightPython", () => {
  it("keeps every character of the source", () => {
    const source = 'def greet(name):\n    return f"Hi {name}"  # done\n';
    expect(
      highlightPython(source)
        .map((span) => span.text)
        .join(""),
    ).toBe(source);
  });

  it("tags keywords, strings, and comments", () => {
    const classes = highlightPython('if x: print("y")  # z').map((span) => span.className);
    expect(classes).toEqual(expect.arrayContaining(["tk-keyword", "tk-string", "tk-comment"]));
  });
});

describe("parse", () => {
  it("maps paths to pages", () => {
    expect(parse("/learn/first-light")).toEqual({ page: "learn", id: "first-light" });
    expect(parse("/review/first-programs")).toEqual({
      page: "review-session",
      chapter: "first-programs",
    });
    expect(parse("/nowhere")).toEqual({ page: "home" });
  });
});
