"use client";

import { profile } from "@/data/profile";

type Mode = "chat" | "jd" | "work" | "meet";

type Props = {
  name: string;
  mode?: Mode;
  onModeChange?: (mode: Mode) => void;
  onBack?: () => void;
};

export function SiteHeader({ name, mode, onModeChange, onBack }: Props) {
  return (
    <header className="sticky top-0 z-30 h-16 flex items-center justify-between gap-3 px-4 sm:px-8 border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--bg)_90%,transparent)] backdrop-blur-md">
      <div className="flex items-center gap-3 min-w-0">
        {onBack ? (
          <button
            type="button"
            onClick={onBack}
            className="text-sm font-medium text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
          >
            ← Home
          </button>
        ) : null}
        <div className="font-display text-[1.02rem] font-semibold tracking-tight truncate">
          {mode ? (
            <>
              <span className="text-[var(--coral)]">{profile.aiName}</span>
              <span className="text-[var(--muted)] font-medium"> · </span>
              <span>{name}</span>
            </>
          ) : (
            name
          )}
        </div>
      </div>

      {mode && onModeChange ? (
        <div className="flex p-1 rounded-full border border-[var(--line)] bg-white overflow-x-auto max-w-[72vw]">
          {(
            [
              ["chat", "Chat"],
              ["work", "Work"],
              ["jd", "Fit"],
              ["meet", "Meet"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() => onModeChange(id)}
              className={[
                "min-h-9 px-3 sm:px-3.5 rounded-full text-sm font-semibold transition-colors whitespace-nowrap",
                mode === id
                  ? "bg-[var(--coral)] text-white"
                  : "text-[var(--muted)] hover:text-[var(--ink)]",
              ].join(" ")}
            >
              {label}
            </button>
          ))}
        </div>
      ) : null}
    </header>
  );
}
