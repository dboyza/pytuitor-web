import type { CheckEvent } from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

// Writes carry a custom header; the server refuses cross-site requests without it.
export async function api<T>(path: string, body?: unknown, method?: "POST" | "PUT"): Promise<T> {
  const write = body !== undefined;
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method: method ?? (write ? "POST" : "GET"),
      credentials: "same-origin",
      headers: write ? { "content-type": "application/json", "x-pytuitor": "1" } : undefined,
      body: write ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(
      "Pytuitor is not responding. Check that it is still running in your terminal.",
      0,
    );
  }
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      if (typeof data.detail === "string") detail = data.detail;
    } catch {
      // Keep the status text.
    }
    throw new ApiError(detail, response.status);
  }
  return response.json() as Promise<T>;
}

/** Read newline-delimited JSON events until the stream ends or the signal aborts. */
export async function streamEvents(
  path: string,
  onEvent: (event: CheckEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`/api${path}`, {
    method: "POST",
    credentials: "same-origin",
    headers: { "x-pytuitor": "1" },
    signal,
  });
  if (!response.ok || !response.body) {
    let detail = response.statusText;
    try {
      detail = (await response.json()).detail ?? detail;
    } catch {
      // Keep the status text.
    }
    throw new ApiError(detail, response.status);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let newline: number;
    while ((newline = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, newline).trim();
      buffer = buffer.slice(newline + 1);
      if (line) onEvent(JSON.parse(line) as CheckEvent);
    }
  }
}

export function download(path: string) {
  const link = document.createElement("a");
  link.href = `/api${path}`;
  link.rel = "noopener";
  document.body.append(link);
  link.click();
  link.remove();
}
