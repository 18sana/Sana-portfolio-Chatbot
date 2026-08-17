"use client";

import { FormEvent, useState } from "react";
import { motion, useReducedMotion } from "motion/react";

type JDResult = {
  match_score: number;
  matched_skills: string[];
  gaps: string[];
  explanation: string;
  injection_attempt_detected?: boolean;
};

type InputMode = "paste" | "upload";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function JDMatchPanel() {
  const [mode, setMode] = useState<InputMode>("paste");
  const [jdText, setJdText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<JDResult | null>(null);
  const reduced = useReducedMotion();

  const canSubmit =
    mode === "paste" ? jdText.trim().length >= 40 : Boolean(file);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const body = new FormData();
      if (mode === "upload" && file) {
        body.append("file", file);
      } else {
        body.append("jd_text", jdText.trim());
      }
      const res = await fetch(`${apiBase}/jd-match`, { method: "POST", body });
      if (!res.ok) {
        const payload = await res.json().catch(() => ({}));
        const detail =
          typeof payload.detail === "string"
            ? payload.detail
            : payload.message || `Request failed (${res.status})`;
        throw new Error(detail);
      }
      setResult((await res.json()) as JDResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Match failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 sm:space-y-7">
      <div>
        <h2 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-[var(--ink)]">
          Job fit
        </h2>
        <p className="text-sm sm:text-base text-[var(--muted)] mt-2 max-w-xl leading-relaxed">
          Paste a JD or upload a file — get a scored report with matched skills, gaps, and a clear
          explanation.
        </p>
      </div>

      <form
        onSubmit={onSubmit}
        className="rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-4 sm:p-6 space-y-5 shadow-[var(--shadow)]"
      >
        <div className="flex p-1 rounded-full border border-[var(--line)] bg-[var(--bg)] w-full sm:w-fit">
          {(
            [
              ["paste", "Paste text"],
              ["upload", "Upload file"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() => setMode(id)}
              className={[
                "flex-1 sm:flex-none min-h-9 px-3 sm:px-4 rounded-full text-sm font-semibold transition-colors",
                mode === id
                  ? "bg-[var(--coral)] text-white"
                  : "text-[var(--muted)] hover:text-[var(--ink)]",
              ].join(" ")}
            >
              {label}
            </button>
          ))}
        </div>

        {mode === "paste" ? (
          <label className="block space-y-2">
            <span className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
              Job description
            </span>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              rows={10}
              placeholder="Paste the full job description here…"
              className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3.5 py-3 outline-none resize-y min-h-[10rem] sm:min-h-[12rem] text-[16px] sm:text-base text-[var(--ink)] placeholder:text-[var(--muted)] focus:border-[var(--coral)] leading-relaxed"
            />
            <span className="text-xs text-[var(--muted)]">
              {jdText.trim().length < 40
                ? `Need a bit more text (${jdText.trim().length}/40)`
                : `${jdText.trim().length.toLocaleString()} characters`}
            </span>
          </label>
        ) : (
          <label className="block space-y-2">
            <span className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
              Document
            </span>
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md,application/pdf,text/plain"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-[var(--ink-soft)] file:mr-3 file:mb-2 sm:file:mb-0 file:min-h-10 file:rounded-full file:border-0 file:bg-[var(--coral-soft)] file:px-4 file:font-semibold file:text-[var(--coral)]"
            />
          </label>
        )}

        <button type="submit" disabled={!canSubmit || loading} className="btn-primary w-full sm:w-auto">
          {loading ? "Analyzing…" : "Run match"}
        </button>
        {error ? <p className="text-[var(--danger)] text-sm">{error}</p> : null}
      </form>

      {result ? (
        <motion.section
          className="rounded-[1.25rem] border border-[var(--line)] overflow-hidden bg-[var(--panel)] shadow-[var(--shadow)]"
          initial={reduced ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="grid sm:grid-cols-[140px_1fr]">
            <div className="p-5 sm:p-6 bg-[var(--coral)] text-white flex flex-row sm:flex-col items-baseline sm:justify-center gap-3 sm:gap-0">
              <div className="text-xs uppercase tracking-[0.18em] opacity-90">Score</div>
              <div className="font-display text-4xl sm:text-5xl font-bold sm:mt-1">
                {Math.round(result.match_score)}
              </div>
            </div>
            <div className="p-5 sm:p-6">
              <h3 className="font-semibold mb-2">Assessment</h3>
              <p className="text-sm sm:text-base text-[var(--muted)] leading-relaxed break-words">
                {result.explanation}
              </p>
            </div>
          </div>
          <div className="grid sm:grid-cols-2 border-t border-[var(--line)]">
            <div className="p-5 sm:p-6 border-b sm:border-b-0 sm:border-r border-[var(--line)]">
              <h4 className="text-xs uppercase tracking-[0.18em] text-[var(--muted)] mb-3">
                Matched
              </h4>
              <ul className="space-y-2 text-sm sm:text-base text-[var(--ink)]">
                {result.matched_skills.map((s) => (
                  <li key={s} className="break-words">
                    {s}
                  </li>
                ))}
              </ul>
            </div>
            <div className="p-5 sm:p-6">
              <h4 className="text-xs uppercase tracking-[0.18em] text-[var(--muted)] mb-3">Gaps</h4>
              <ul className="space-y-2 text-sm sm:text-base text-[var(--ink)]">
                {result.gaps.map((s) => (
                  <li key={s} className="break-words">
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </motion.section>
      ) : null}
    </div>
  );
}
