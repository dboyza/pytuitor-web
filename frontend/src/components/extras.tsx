import { useEffect, useRef, useState, type ReactNode } from "react";
import { api } from "../api";
import { useApp } from "../context";
import { ConsoleView } from "../terminal/ConsoleView";
import type { ConsoleSession } from "../types";
import { Dialog } from "./ui";

export type MenuItem =
  | {
      label: string;
      icon?: ReactNode;
      onSelect: () => void;
      danger?: boolean;
      hint?: string;
    }
  | "divider";

export function Menu({
  trigger,
  items,
  label,
}: {
  trigger: ReactNode;
  items: MenuItem[];
  label: string;
}) {
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const dismiss = (event: Event) => {
      if (event instanceof KeyboardEvent && event.key !== "Escape") return;
      if (event instanceof PointerEvent && root.current?.contains(event.target as Node)) return;
      setOpen(false);
    };
    window.addEventListener("pointerdown", dismiss);
    window.addEventListener("keydown", dismiss);
    return () => {
      window.removeEventListener("pointerdown", dismiss);
      window.removeEventListener("keydown", dismiss);
    };
  }, [open]);
  return (
    <div className="menu-anchor" ref={root}>
      <button
        className="icon-btn"
        aria-label={label}
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        {trigger}
      </button>
      {open && (
        <div className="menu" role="menu" aria-label={label}>
          {items.map((item, index) =>
            item === "divider" ? (
              <hr key={index} />
            ) : (
              <button
                key={item.label}
                role="menuitem"
                className={`menu-item ${item.danger ? "danger" : ""}`}
                onClick={() => {
                  setOpen(false);
                  item.onSelect();
                }}
              >
                {item.icon}
                <span>{item.label}</span>
                {item.hint && <span className="menu-hint">{item.hint}</span>}
              </button>
            ),
          )}
        </div>
      )}
    </div>
  );
}

/** A working game version in a temporary folder; closing ends its process. */
export function PlayDialog({
  checkpoint,
  title,
  onClose,
}: {
  checkpoint: string;
  title: string;
  onClose: () => void;
}) {
  const { theme, fail } = useApp();
  const [session, setSession] = useState<ConsoleSession | null>(null);
  const [ended, setEnded] = useState(false);
  const opened = useRef<string | null>(null);
  useEffect(() => {
    let alive = true;
    api<ConsoleSession>(`/game/checkpoints/${checkpoint}/play`, {
      cols: 96,
      rows: 26,
    })
      .then((created) => {
        opened.current = created.id;
        if (alive) setSession(created);
        else void api(`/consoles/${created.id}/close`, {});
      })
      .catch((error) => {
        fail(error);
        onClose();
      });
    return () => {
      alive = false;
      if (opened.current) void api(`/consoles/${opened.current}/close`, {}).catch(() => undefined);
    };
    // Each dialog plays one checkpoint once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [checkpoint]);
  return (
    <Dialog title={`Play · ${title}`} onClose={onClose} wide className="play-dialog">
      <p className="muted">
        A temporary copy of this working version. Your drafts and history stay unchanged.
        {ended && " The game has finished."}
      </p>
      <div className="play-surface">
        {session && (
          <ConsoleView
            session={session}
            active
            theme={theme}
            fontSize={14}
            onEnded={() => setEnded(true)}
          />
        )}
      </div>
    </Dialog>
  );
}

const COLORS = ["#3776ab", "#5b9fe0", "#ffd343", "#ffe58a", "#4cc38a"];
// A fixed, pseudo-random spread keeps rendering pure.
const noise = (index: number, salt: number) => {
  const value = Math.sin(index * 12.9898 + salt * 78.233) * 43758.5453;
  return value - Math.floor(value);
};
const PIECES = Array.from({ length: 36 }, (_, index) => ({
  left: 50 + (noise(index, 1) - 0.5) * 30,
  x: (noise(index, 2) - 0.5) * 520,
  y: -(160 + noise(index, 3) * 260),
  rotate: noise(index, 4) * 720 - 360,
  delay: noise(index, 5) * 120,
  color: COLORS[index % COLORS.length],
  wide: noise(index, 6) > 0.5,
}));

export function Confetti() {
  return (
    <div className="confetti" aria-hidden="true">
      {PIECES.map((piece, index) => (
        <span
          key={index}
          style={
            {
              left: `${piece.left}%`,
              background: piece.color,
              width: piece.wide ? 10 : 6,
              animationDelay: `${piece.delay}ms`,
              "--x": `${piece.x}px`,
              "--y": `${piece.y}px`,
              "--r": `${piece.rotate}deg`,
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  );
}

/** A draggable divider that reports pointer movement in pixels. */
export function Splitter({
  direction,
  onDrag,
  onDone,
  label,
}: {
  direction: "row" | "column";
  onDrag: (position: number) => void;
  onDone?: () => void;
  label: string;
}) {
  return (
    <div
      className={`splitter ${direction}`}
      role="separator"
      aria-orientation={direction === "row" ? "vertical" : "horizontal"}
      aria-label={label}
      onPointerDown={(event) => {
        event.preventDefault();
        const target = event.currentTarget;
        target.setPointerCapture(event.pointerId);
        document.body.classList.add(direction === "row" ? "resizing-x" : "resizing-y");
        const move = (moved: PointerEvent) =>
          onDrag(direction === "row" ? moved.clientX : moved.clientY);
        const up = () => {
          target.removeEventListener("pointermove", move);
          target.removeEventListener("pointerup", up);
          document.body.classList.remove("resizing-x", "resizing-y");
          onDone?.();
        };
        target.addEventListener("pointermove", move);
        target.addEventListener("pointerup", up);
      }}
    />
  );
}
