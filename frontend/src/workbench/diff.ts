export type DiffLine = { kind: "same" | "add" | "remove"; text: string };

/** A line diff from the longest common subsequence; lesson files are small enough for O(n·m). */
export function diffLines(before: string, after: string): DiffLine[] {
  const a = before.replace(/\n$/, "").split("\n");
  const b = after.replace(/\n$/, "").split("\n");
  if (before === "") a.length = 0;
  if (after === "") b.length = 0;
  const table = Array.from({ length: a.length + 1 }, () => new Uint32Array(b.length + 1));
  for (let i = a.length - 1; i >= 0; i--)
    for (let j = b.length - 1; j >= 0; j--)
      table[i][j] =
        a[i] === b[j] ? table[i + 1][j + 1] + 1 : Math.max(table[i + 1][j], table[i][j + 1]);
  const lines: DiffLine[] = [];
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) {
      lines.push({ kind: "same", text: a[i] });
      i++;
      j++;
    } else if (table[i + 1][j] >= table[i][j + 1]) lines.push({ kind: "remove", text: a[i++] });
    else lines.push({ kind: "add", text: b[j++] });
  }
  while (i < a.length) lines.push({ kind: "remove", text: a[i++] });
  while (j < b.length) lines.push({ kind: "add", text: b[j++] });
  return lines;
}
