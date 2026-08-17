"use client";

import { FormEvent, useMemo, useState } from "react";
import { motion, useReducedMotion } from "motion/react";
import { profile } from "@/data/profile";

const TIME_OPTIONS = [
  "9:30 AM",
  "10:00 AM",
  "10:30 AM",
  "11:00 AM",
  "11:30 AM",
  "12:00 PM",
  "2:00 PM",
  "2:30 PM",
  "3:00 PM",
  "3:30 PM",
  "4:00 PM",
  "4:30 PM",
  "5:00 PM",
  "5:30 PM",
  "6:00 PM",
  "6:30 PM",
  "7:00 PM",
] as const;

type ProposedSlot = {
  date: string;
  time: string;
};

type FormState = {
  name: string;
  company: string;
  role: string;
  email: string;
  note: string;
  slots: ProposedSlot[];
};

function todayISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function formatSlot(slot: ProposedSlot) {
  if (!slot.date || !slot.time) return null;
  const [y, m, d] = slot.date.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  const weekday = dt.toLocaleDateString(undefined, { weekday: "short" });
  const niceDate = dt.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
  return `${weekday}, ${niceDate} · ${slot.time} ${profile.timezone}`;
}

function buildBrief(form: FormState) {
  const proposals = form.slots
    .map(formatSlot)
    .filter((s): s is string => Boolean(s));

  return [
    `Intro request via ${profile.aiName}`,
    "",
    `From: ${form.name}`,
    form.company ? `Company: ${form.company}` : null,
    form.role ? `Role discussing: ${form.role}` : null,
    form.email ? `Reply-to: ${form.email}` : null,
    "",
    "Proposed times (recruiter availability — please confirm one):",
    ...(proposals.length
      ? proposals.map((p, i) => `  ${i + 1}. ${p}`)
      : ["  (none selected)"]),
    "",
    form.note ? `Context:\n${form.note}` : "Context: (none added)",
    "",
    "— Sent from Sana’s portfolio",
  ]
    .filter((line) => line !== null)
    .join("\n");
}

const emptySlot = (): ProposedSlot => ({ date: todayISO(), time: "3:00 PM" });

export function MeetPanel() {
  const reduced = useReducedMotion();
  const [form, setForm] = useState<FormState>({
    name: "",
    company: "",
    role: "",
    email: "",
    note: "",
    slots: [emptySlot(), emptySlot()],
  });
  const [copied, setCopied] = useState(false);

  const brief = useMemo(() => buildBrief(form), [form]);
  const validSlots = form.slots.filter((s) => s.date && s.time);
  const canSend = form.name.trim().length > 1 && validSlots.length >= 1;

  function updateField<K extends keyof Omit<FormState, "slots">>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function updateSlot(index: number, patch: Partial<ProposedSlot>) {
    setForm((prev) => ({
      ...prev,
      slots: prev.slots.map((s, i) => (i === index ? { ...s, ...patch } : s)),
    }));
  }

  function addSlot() {
    if (form.slots.length >= 3) return;
    setForm((prev) => ({ ...prev, slots: [...prev.slots, emptySlot()] }));
  }

  function removeSlot(index: number) {
    if (form.slots.length <= 1) return;
    setForm((prev) => ({
      ...prev,
      slots: prev.slots.filter((_, i) => i !== index),
    }));
  }

  function onEmail(e: FormEvent) {
    e.preventDefault();
    if (!canSend) return;
    const subject = encodeURIComponent(
      `Intro with ${profile.fullName}${form.company ? ` — ${form.company}` : ""}`,
    );
    const body = encodeURIComponent(brief);
    window.location.href = `mailto:${profile.email}?subject=${subject}&body=${body}`;
  }

  async function onCopy() {
    try {
      await navigator.clipboard.writeText(brief);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <p className="text-[0.7rem] uppercase tracking-[0.28em] text-[var(--muted)] mb-2">
          {profile.aiName} · Meet
        </p>
        <h2 className="font-display text-3xl font-semibold tracking-tight text-[var(--ink)]">
          Propose a time
        </h2>
        <p className="mt-2 text-[var(--muted)] max-w-xl leading-relaxed">
          We can’t see your calendar from here — pick 1–3 times that work for{" "}
          <em>you</em>. {profile.fullName.split(" ")[0]} confirms one. Times are in{" "}
          {profile.timezone}.
        </p>
      </div>

      {profile.bookingUrl ? (
        <motion.a
          href={profile.bookingUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary"
          initial={reduced ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Or book on live calendar
          <span aria-hidden>↗</span>
        </motion.a>
      ) : null}

      <form
        onSubmit={onEmail}
        className="rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-5 sm:p-6 shadow-[var(--shadow)] space-y-5"
      >
        <div className="grid sm:grid-cols-2 gap-4">
          <label className="block space-y-1.5">
            <span className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
              Your name
            </span>
            <input
              required
              value={form.name}
              onChange={(e) => updateField("name", e.target.value)}
              className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3.5 py-2.5 outline-none focus:border-[var(--coral)]"
              placeholder="Alex Chen"
            />
          </label>
          <label className="block space-y-1.5">
            <span className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
              Work email
            </span>
            <input
              type="email"
              value={form.email}
              onChange={(e) => updateField("email", e.target.value)}
              className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3.5 py-2.5 outline-none focus:border-[var(--coral)]"
              placeholder="alex@company.com"
            />
          </label>
          <label className="block space-y-1.5">
            <span className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
              Company
            </span>
            <input
              value={form.company}
              onChange={(e) => updateField("company", e.target.value)}
              className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3.5 py-2.5 outline-none focus:border-[var(--coral)]"
              placeholder="Acme"
            />
          </label>
          <label className="block space-y-1.5">
            <span className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
              Role / team
            </span>
            <input
              value={form.role}
              onChange={(e) => updateField("role", e.target.value)}
              className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3.5 py-2.5 outline-none focus:border-[var(--coral)]"
              placeholder="Backend / AI platform"
            />
          </label>
        </div>

        <fieldset className="space-y-3">
          <legend className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
            Times that work for you
          </legend>
          <div className="space-y-3">
            {form.slots.map((slot, index) => (
              <div
                key={index}
                className="flex flex-col sm:flex-row sm:items-end gap-3 rounded-xl border border-[var(--line)] bg-[var(--bg)] p-3.5"
              >
                <div className="text-sm font-semibold text-[var(--coral)] sm:w-8 shrink-0 pb-2.5">
                  {index + 1}
                </div>
                <label className="block space-y-1.5 flex-1 min-w-0">
                  <span className="text-xs text-[var(--muted)]">Date</span>
                  <input
                    type="date"
                    min={todayISO()}
                    required
                    value={slot.date}
                    onChange={(e) => updateSlot(index, { date: e.target.value })}
                    className="w-full rounded-xl border border-[var(--line)] bg-white px-3 py-2.5 outline-none focus:border-[var(--coral)]"
                  />
                </label>
                <label className="block space-y-1.5 flex-1 min-w-0">
                  <span className="text-xs text-[var(--muted)]">Time ({profile.timezone})</span>
                  <select
                    value={slot.time}
                    onChange={(e) => updateSlot(index, { time: e.target.value })}
                    className="w-full rounded-xl border border-[var(--line)] bg-white px-3 py-2.5 outline-none focus:border-[var(--coral)]"
                  >
                    {TIME_OPTIONS.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </label>
                {form.slots.length > 1 ? (
                  <button
                    type="button"
                    onClick={() => removeSlot(index)}
                    className="min-h-10 px-3 text-sm font-semibold text-[var(--muted)] hover:text-[var(--danger)] transition-colors"
                  >
                    Remove
                  </button>
                ) : null}
              </div>
            ))}
          </div>
          {form.slots.length < 3 ? (
            <button
              type="button"
              onClick={addSlot}
              className="text-sm font-semibold text-[var(--coral)] hover:underline"
            >
              + Add another option
            </button>
          ) : null}
        </fieldset>

        <label className="block space-y-1.5">
          <span className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
            Why this chat? (optional)
          </span>
          <textarea
            value={form.note}
            onChange={(e) => updateField("note", e.target.value)}
            rows={3}
            className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3.5 py-2.5 outline-none resize-none focus:border-[var(--coral)]"
            placeholder="We’re hiring for X. Curious about your RAG / agent work…"
          />
        </label>

        <div className="flex flex-wrap gap-3 pt-1">
          <button type="submit" disabled={!canSend} className="btn-primary">
            Email proposals
            <span aria-hidden>→</span>
          </button>
          <button type="button" onClick={onCopy} disabled={!canSend} className="btn-secondary">
            {copied ? "Copied" : "Copy briefing"}
          </button>
        </div>
      </form>
    </div>
  );
}
