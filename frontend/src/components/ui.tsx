import { useEffect, useRef, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { Check, CircleDashed, X } from "lucide-react";
import type { Status } from "../types";
import { useApp } from "../context";

export function Logo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 128 128" aria-hidden="true" className="logo">
      <rect width="128" height="128" rx="30" fill="var(--logo-bg, #171a1e)" />
      <path d="M64 38C51 29 34 27 20 31V91C35 87 51 89 64 98V38Z" fill="#3776AB" />
      <path d="M64 38C77 29 94 27 108 31V91C93 87 77 89 64 98V38Z" fill="#FFD343" />
      <path
        d="M34 49L45 59L34 69"
        stroke="#F4F5F6"
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path d="M78 70H94" stroke="#171a1e" strokeWidth="6" strokeLinecap="round" />
      <path d="M64 39V97" stroke="#171a1e" strokeWidth="4" />
    </svg>
  );
}

export function StatusIcon({ status, size = 18 }: { status: Status; size?: number }) {
  const label = {
    new: "Not started",
    "in progress": "In progress",
    familiar: "Known topic",
    completed: "Completed",
  }[status];
  return (
    <span
      className={`status-icon ${status.replace(" ", "-")}`}
      style={{ width: size, height: size }}
      role="img"
      aria-label={label}
      title={label}
    >
      {status === "completed" && <Check size={size * 0.62} strokeWidth={3} />}
      {status === "familiar" && <Check size={size * 0.62} strokeWidth={2.5} />}
      {status === "in progress" && <span className="half" />}
      {status === "new" && <CircleDashed size={size} strokeWidth={1.6} />}
    </span>
  );
}

export function ProgressRing({
  value,
  total,
  size = 64,
  stroke = 6,
  tone = "blue",
  children,
}: {
  value: number;
  total: number;
  size?: number;
  stroke?: number;
  tone?: "blue" | "yellow" | "green";
  children?: ReactNode;
}) {
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const share = total ? Math.min(1, value / total) : 0;
  return (
    <div className="ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} aria-hidden="true">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={stroke}
          className="ring-track"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={stroke}
          className={`ring-value ${tone}`}
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - share)}
        />
      </svg>
      <div className="ring-label">{children}</div>
    </div>
  );
}

export function Dialog({
  title,
  onClose,
  children,
  footer,
  wide,
  className = "",
}: {
  title: ReactNode;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
  wide?: boolean;
  className?: string;
}) {
  const panel = useRef<HTMLDivElement>(null);
  const close = useRef(onClose);
  useEffect(() => {
    close.current = onClose;
  });
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const first = panel.current?.querySelector<HTMLElement>(
      "[data-autofocus], input, textarea, button.primary, button",
    );
    first?.focus();
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        close.current();
      }
      if (event.key !== "Tab" || !panel.current) return;
      const items = [
        ...panel.current.querySelectorAll<HTMLElement>(
          "button:not(:disabled), input, textarea, select, [tabindex='0'], a[href]",
        ),
      ];
      if (!items.length) return;
      const [head, tail] = [items[0], items[items.length - 1]];
      if (event.shiftKey && document.activeElement === head) {
        event.preventDefault();
        tail.focus();
      } else if (!event.shiftKey && document.activeElement === tail) {
        event.preventDefault();
        head.focus();
      }
    };
    window.addEventListener("keydown", key, true);
    return () => {
      window.removeEventListener("keydown", key, true);
      previous?.focus?.();
    };
  }, []);
  return createPortal(
    <div
      className="scrim"
      onMouseDown={(event) => event.target === event.currentTarget && onClose()}
    >
      <div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-label={typeof title === "string" ? title : undefined}
        className={`dialog ${wide ? "wide" : ""} ${className}`}
      >
        <header className="dialog-head">
          <h2>{title}</h2>
          <button className="icon-btn" aria-label="Close" onClick={onClose}>
            <X size={17} />
          </button>
        </header>
        <div className="dialog-body">{children}</div>
        {footer && <footer className="dialog-foot">{footer}</footer>}
      </div>
    </div>,
    document.body,
  );
}

/** Render page-specific controls into the shared top bar. */
export function TopBarSlot({ children }: { children: ReactNode }) {
  const { topbar } = useApp();
  return topbar ? createPortal(children, topbar) : null;
}

export function Kbd({ children }: { children: ReactNode }) {
  return <kbd className="kbd">{children}</kbd>;
}

export function Spinner({ size = 14 }: { size?: number }) {
  return (
    <span
      className="spinner"
      style={{ width: size, height: size }}
      role="status"
      aria-label="Working"
    />
  );
}

export function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KiB`;
}
