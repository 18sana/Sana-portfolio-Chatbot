"use client";

import { FormEvent, useState } from "react";
import { profile } from "@/data/profile";

type Citation = {
  chunk_id: string;
  document_id: string;
  section_title?: string | null;
  source_title?: string | null;
  snippet: string;
  score?: number | null;
};

type Msg = {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  grounded?: boolean | null;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const SUGGESTIONS = [
  "What have you built?",
  "Tell me about RAG-Agent",
  "What’s your strongest AI project?",
];

type Props = {
  onBookMeet?: () => void;
};

export function ChatPanel({ onBookMeet }: Props) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [sessionId] = useState(() => `web-${Math.random().toString(36).slice(2, 10)}`);
  const [openCitation, setOpenCitation] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setStreaming(true);

    let assistant = "";
    let citations: Citation[] = [];
    let grounded: boolean | null = null;
    setMessages((m) => [...m, { role: "assistant", content: "" }]);

    try {
      const res = await fetch(`${apiBase}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });
      if (!res.ok || !res.body) throw new Error(`Chat failed (${res.status})`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";
        for (const part of parts) {
          const lines = part.split("\n");
          const eventLine = lines.find((l) => l.startsWith("event:"));
          const dataLine = lines.find((l) => l.startsWith("data:"));
          if (!eventLine || !dataLine) continue;
          const event = eventLine.replace("event:", "").trim();
          const data = JSON.parse(dataLine.replace("data:", "").trim());
          if (event === "token") {
            assistant += data;
            setMessages((m) => {
              const copy = [...m];
              copy[copy.length - 1] = { role: "assistant", content: assistant, citations, grounded };
              return copy;
            });
          }
          if (event === "citations") citations = data;
          if (event === "final") {
            assistant = data.answer || assistant;
            citations = data.citations || citations;
            grounded = data.grounded;
            setMessages((m) => {
              const copy = [...m];
              copy[copy.length - 1] = { role: "assistant", content: assistant, citations, grounded };
              return copy;
            });
          }
          if (event === "error") throw new Error(data.message || "stream error");
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Request failed";
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = {
          role: "assistant",
          content: `I couldn’t complete that request (${message}). Check the API is running and try again.`,
        };
        return copy;
      });
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="flex flex-col min-h-[min(62vh,100dvh-10rem)] sm:min-h-[68vh] gap-5 sm:gap-6">
      <div className="flex-1 space-y-4 sm:space-y-5">
        {messages.length === 0 ? (
          <div className="rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-5 sm:p-7 shadow-[var(--shadow)]">
            <h2 className="font-display text-xl sm:text-2xl font-semibold tracking-tight text-[var(--ink)]">
              Ask {profile.aiName} anything
            </h2>
            <p className="mt-2 text-sm sm:text-base text-[var(--muted)] leading-relaxed max-w-md">
              Experience, stack, projects, impact — answers stream with sources you can expand.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              {SUGGESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  className="min-h-10 px-3.5 rounded-full border border-[var(--line)] bg-[var(--bg)] text-sm text-[var(--ink-soft)] hover:border-[var(--coral)] hover:text-[var(--coral)] transition-colors"
                  onClick={() => setInput(q)}
                >
                  {q}
                </button>
              ))}
              {onBookMeet ? (
                <button
                  type="button"
                  className="min-h-10 px-3.5 rounded-full border border-[var(--coral)] bg-[var(--coral-soft)] text-sm font-semibold text-[var(--coral)] hover:bg-[var(--coral)] hover:text-white transition-colors"
                  onClick={onBookMeet}
                >
                  Book an intro
                </button>
              ) : null}
            </div>
          </div>
        ) : null}

        {messages.map((msg, idx) => (
          <article
            key={`${msg.role}-${idx}`}
            className={
              msg.role === "user"
                ? "ml-auto max-w-[min(100%,22rem)] sm:max-w-[82%] rounded-2xl rounded-br-md bg-[var(--coral-soft)] px-3.5 sm:px-4 py-3 text-[var(--ink)] break-words"
                : "mr-auto w-full sm:max-w-[92%] rounded-2xl rounded-bl-md border border-[var(--line)] bg-[var(--panel)] px-3.5 sm:px-4 py-3 shadow-sm break-words"
            }
          >
            <div className="text-[0.65rem] uppercase tracking-[0.18em] text-[var(--muted)] mb-1.5">
              {msg.role === "user" ? "You" : profile.aiName}
              {msg.role === "assistant" && msg.grounded === false ? " · needs review" : ""}
            </div>
            <div
              className={`whitespace-pre-wrap leading-relaxed text-[0.95rem] sm:text-base break-words [overflow-wrap:anywhere] ${
                streaming && idx === messages.length - 1 ? "stream-caret" : ""
              }`}
            >
              {msg.content}
            </div>
            {msg.citations && msg.citations.length > 0 ? (
              <div className="mt-3">
                <div className="text-[0.62rem] uppercase tracking-[0.16em] text-[var(--muted)] mb-1.5">
                  Sources
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {msg.citations.map((c) => {
                    const open = openCitation === c.chunk_id;
                    const label = c.section_title || c.source_title || "Source";
                    return (
                      <button
                        key={c.chunk_id}
                        type="button"
                        title={c.snippet}
                        className={[
                          "max-w-full truncate rounded-full border px-2.5 py-1 text-xs font-semibold transition-colors",
                          open
                            ? "border-[var(--coral)] bg-[var(--coral-soft)] text-[var(--coral)]"
                            : "border-[var(--line)] bg-[var(--bg)] text-[var(--ink-soft)] hover:border-[var(--coral)] hover:text-[var(--coral)]",
                        ].join(" ")}
                        onClick={() => setOpenCitation(open ? null : c.chunk_id)}
                      >
                        {label}
                      </button>
                    );
                  })}
                </div>
                {msg.citations.map((c) =>
                  openCitation === c.chunk_id ? (
                    <p
                      key={`${c.chunk_id}-snippet`}
                      className="mt-2 rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--muted)] leading-relaxed break-words"
                    >
                      {c.snippet}
                    </p>
                  ) : null,
                )}
              </div>
            ) : null}
          </article>
        ))}
      </div>

      <form
        onSubmit={onSubmit}
        className="sticky bottom-[max(0.75rem,env(safe-area-inset-bottom))] sm:bottom-4 rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-2 sm:p-2.5 shadow-[var(--shadow)]"
      >
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={2}
            placeholder="Ask about experience, projects, stack…"
            className="flex-1 min-w-0 bg-transparent px-2.5 sm:px-3 py-2.5 outline-none resize-none text-[16px] sm:text-base text-[var(--ink)] placeholder:text-[var(--muted)]"
          />
          <button
            type="submit"
            disabled={streaming}
            className="btn-primary shrink-0 !min-h-11 !px-4 sm:!px-5"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
