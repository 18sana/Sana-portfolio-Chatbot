"use client";

import { profile } from "@/data/profile";
import { AshMark } from "@/components/AshMark";

type Mode = "chat" | "jd" | "work" | "meet";

type Props = {
  name: string;
  mode?: Mode;
  onModeChange?: (mode: Mode) => void;
  onBack?: () => void;
};

export function SiteHeader({ name, mode, onModeChange, onBack }: Props) {
  const modes = (
    [
      ["chat", "Chat"],
      ["work", "Work"],
      ["jd", "Fit"],
      ["meet", "Meet"],
    ] as const
  );

  return (
    <header className="sticky top-0 z-30 border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--bg)_90%,transparent)] backdrop-blur-md pt-[env(safe-area-inset-top)]">
      <div className="flex items-center justify-between gap-2 sm:gap-3 px-3 sm:px-8 min-h-14 sm:h-16 py-2">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          {onBack ? (
            <button
              type="button"
              onClick={onBack}
              className="shrink-0 text-sm font-medium text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
              aria-label="Back to home"
            >
              <span className="sm:hidden">←</span>
              <span className="hidden sm:inline">← Home</span>
            </button>
          ) : null}
          <div className="flex items-center gap-2 min-w-0">
            <AshMark size={28} className="shrink-0 rounded-[0.55rem] shadow-sm" />
            <div className="font-display text-[0.95rem] sm:text-[1.02rem] font-semibold tracking-tight truncate">
              {mode ? (
                <>
                  <span className="text-[var(--coral)]">{profile.aiName}</span>
                  <span className="hidden sm:inline text-[var(--muted)] font-medium"> · </span>
                  <span className="hidden sm:inline">{name}</span>
                </>
              ) : (
                <>
                  <span className="text-[var(--coral)]">{profile.aiName}</span>
                  <span className="text-[var(--muted)] font-medium"> · </span>
                  <span className="truncate">{name.split(" ")[0]}</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Desktop / tablet: inline mode pills */}
        {mode && onModeChange ? (
          <nav
            className="hidden sm:flex p-1 rounded-full border border-[var(--line)] bg-white overflow-x-auto max-w-[min(72vw,28rem)] scrollbar-none"
            aria-label="Sections"
          >
            {modes.map(([id, label]) => (
              <button
                key={id}
                type="button"
                onClick={() => onModeChange(id)}
                className={[
                  "min-h-9 px-3.5 rounded-full text-sm font-semibold transition-colors whitespace-nowrap",
                  mode === id
                    ? "bg-[var(--coral)] text-white"
                    : "text-[var(--muted)] hover:text-[var(--ink)]",
                ].join(" ")}
              >
                {label}
              </button>
            ))}
          </nav>
        ) : null}
      </div>

      {/* Phone: full-width mode bar under brand */}
      {mode && onModeChange ? (
        <nav
          className="sm:hidden px-3 pb-2.5"
          aria-label="Sections"
        >
          <div className="grid grid-cols-4 gap-1 p-1 rounded-full border border-[var(--line)] bg-white">
            {modes.map(([id, label]) => (
              <button
                key={id}
                type="button"
                onClick={() => onModeChange(id)}
                className={[
                  "min-h-9 rounded-full text-xs font-semibold transition-colors",
                  mode === id
                    ? "bg-[var(--coral)] text-white"
                    : "text-[var(--muted)]",
                ].join(" ")}
              >
                {label}
              </button>
            ))}
          </div>
        </nav>
      ) : null}
    </header>
  );
}
