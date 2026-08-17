"use client";

import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { ChatPanel } from "@/components/ChatPanel";
import { JDMatchPanel } from "@/components/JDMatchPanel";
import { MeetPanel } from "@/components/MeetPanel";
import { PortfolioPanel } from "@/components/PortfolioPanel";
import { SiteHeader } from "@/components/SiteHeader";
import { profile } from "@/data/profile";

type Mode = "chat" | "jd" | "work" | "meet";

type PreviewMsg = {
  role: "user" | "assistant";
  text: string;
  title?: string;
};

const PREVIEW: PreviewMsg[] = [
  { role: "user", text: "What kind of work do you do?" },
  {
    role: "assistant",
    text: "I’m a software developer focused on full-stack product work and AI agent platforms — currently at Syvora.",
  },
  { role: "user", text: "Any projects I should know about?" },
  {
    role: "assistant",
    title: "RAG-Agent",
    text: "Built so companies can trust AI assistants with their own documents — answers stay grounded in real sources, across teams and workspaces, instead of guessing.",
  },
];

export default function Home() {
  const [mode, setMode] = useState<Mode>("chat");
  const [entered, setEntered] = useState(false);
  const reduced = useReducedMotion();
  const appName = process.env.NEXT_PUBLIC_APP_NAME ?? profile.fullName;

  if (!entered) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        <div
          className="pointer-events-none absolute -top-32 -right-24 h-[28rem] w-[28rem] rounded-full blur-3xl opacity-50"
          style={{ background: "radial-gradient(circle, rgba(232,90,58,0.28), transparent 70%)" }}
          aria-hidden
        />
        <div
          className="pointer-events-none absolute bottom-0 left-[-10%] h-[22rem] w-[22rem] rounded-full blur-3xl opacity-40"
          style={{ background: "radial-gradient(circle, rgba(22,21,26,0.06), transparent 70%)" }}
          aria-hidden
        />

        <SiteHeader name={appName} />

        <section className="relative mx-auto max-w-6xl px-5 sm:px-8 pt-10 sm:pt-14 pb-16 grid lg:grid-cols-[1fr_1.05fr] gap-10 lg:gap-14 items-center">
          <div className="max-w-xl">
            <motion.p
              className="text-[0.7rem] uppercase tracking-[0.32em] text-[var(--muted)] mb-4"
              initial={reduced ? false : { opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45 }}
            >
              Meet {profile.aiName} · not another PDF
            </motion.p>

            <motion.h1
              className="font-display font-bold text-[clamp(2.75rem,8vw,4.75rem)] leading-[0.92] tracking-[-0.045em] text-[var(--ink)]"
              initial={reduced ? false : { opacity: 0, y: 22 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1], delay: 0.05 }}
            >
              <span className="text-[var(--coral)]">{profile.aiName}</span>
              <span className="block">knows my work.</span>
            </motion.h1>

            <motion.p
              className="mt-5 text-[1.05rem] leading-relaxed text-[var(--muted)] max-w-[36ch]"
              initial={reduced ? false : { opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.15 }}
            >
              Ask about projects, paste a JD for fit, or book an intro — answers come from real
              sources, not guesswork.
            </motion.p>

            <motion.div
              className="mt-8 flex flex-wrap gap-3"
              initial={reduced ? false : { opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.24 }}
            >
              <button type="button" className="btn-primary" onClick={() => setEntered(true)}>
                Talk to {profile.aiName}
                <span aria-hidden>→</span>
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => {
                  setMode("meet");
                  setEntered(true);
                }}
              >
                Book an intro
              </button>
            </motion.div>

            <motion.div
              className="mt-5 flex flex-wrap gap-2"
              initial={reduced ? false : { opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.35 }}
            >
              <a
                href={profile.resumeUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-semibold text-[var(--ink)] underline underline-offset-4 decoration-[var(--line-strong)] hover:decoration-[var(--coral)] hover:text-[var(--coral)] transition-colors"
              >
                Open resume ↗
              </a>
              <span className="text-[var(--muted)]">·</span>
              <a
                href={profile.githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-semibold text-[var(--ink)] underline underline-offset-4 decoration-[var(--line-strong)] hover:decoration-[var(--coral)] hover:text-[var(--coral)] transition-colors"
              >
                GitHub ↗
              </a>
              <span className="text-[var(--muted)]">·</span>
              <a
                href={profile.linkedinUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-semibold text-[var(--ink)] underline underline-offset-4 decoration-[var(--line-strong)] hover:decoration-[var(--coral)] hover:text-[var(--coral)] transition-colors"
              >
                LinkedIn ↗
              </a>
            </motion.div>
          </div>

          <motion.div
            className="relative"
            initial={reduced ? false : { opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1], delay: 0.18 }}
          >
            <div className="absolute -inset-3 rounded-[2rem] bg-[var(--coral)]/10 blur-2xl" aria-hidden />
            <div className="relative rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel)] shadow-[var(--shadow)] overflow-hidden">
              <div className="flex items-center justify-between px-5 py-3.5 border-b border-[var(--line)] bg-[var(--bg)]">
                <div className="flex items-center gap-2.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-[var(--coral)]" />
                  <span className="text-sm font-semibold text-[var(--ink)]">{profile.aiName}</span>
                </div>
                <span className="text-xs text-[var(--muted)]">Grounded · live</span>
              </div>

              <div className="p-4 sm:p-5 space-y-3.5 min-h-[360px]">
                {PREVIEW.map((msg, i) => (
                  <motion.div
                    key={`${msg.role}-${i}`}
                    className={
                      msg.role === "user"
                        ? "ml-8 rounded-2xl rounded-br-md bg-[var(--coral-soft)] px-3.5 py-2.5 text-sm text-[var(--ink)]"
                        : "mr-4 rounded-2xl rounded-bl-md border border-[var(--line)] bg-white px-3.5 py-2.5 text-sm text-[var(--ink-soft)] leading-relaxed"
                    }
                    initial={reduced ? false : { opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.35 + i * 0.12, duration: 0.4 }}
                  >
                    <div className="text-[0.62rem] uppercase tracking-[0.16em] text-[var(--muted)] mb-1">
                      {msg.role === "user" ? "You" : profile.aiName}
                    </div>
                    {msg.title ? (
                      <div className="font-semibold text-[var(--ink)] mb-1">{msg.title}</div>
                    ) : null}
                    {msg.text}
                  </motion.div>
                ))}
              </div>

              <div className="px-4 pb-4 flex flex-col sm:flex-row gap-2">
                <button
                  type="button"
                  className="btn-primary flex-1"
                  onClick={() => setEntered(true)}
                >
                  Continue with {profile.aiName}
                </button>
                <button
                  type="button"
                  className="btn-secondary flex-1"
                  onClick={() => {
                    setMode("work");
                    setEntered(true);
                  }}
                >
                  Browse projects
                </button>
              </div>
            </div>
          </motion.div>
        </section>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <SiteHeader
        name={appName}
        mode={mode}
        onModeChange={setMode}
        onBack={() => setEntered(false)}
      />
      <main className="px-4 sm:px-8 py-8 max-w-[760px] mx-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={mode}
            initial={reduced ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={reduced ? undefined : { opacity: 0, y: -6 }}
            transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
          >
            {mode === "chat" ? (
              <ChatPanel onBookMeet={() => setMode("meet")} />
            ) : mode === "work" ? (
              <PortfolioPanel />
            ) : mode === "meet" ? (
              <MeetPanel />
            ) : (
              <JDMatchPanel />
            )}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
