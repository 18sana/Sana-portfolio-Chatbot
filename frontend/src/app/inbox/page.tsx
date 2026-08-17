"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import Link from "next/link";

type ConversationSummary = {
  id: string;
  session_id: string;
  message_count: number;
  preview: string | null;
  client_ip: string | null;
  created_at: string;
  updated_at: string;
};

type Message = {
  id: string;
  role: string;
  content: string;
  grounded: boolean | null;
  model: string | null;
  created_at: string;
};

type ConversationDetail = {
  id: string;
  session_id: string;
  client_ip: string | null;
  user_agent: string | null;
  created_at: string;
  updated_at: string;
  messages: Message[];
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const KEY_STORAGE = "ash_admin_key";

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

export default function InboxPage() {
  const [keyInput, setKeyInput] = useState("");
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ConversationDetail | null>(null);

  useEffect(() => {
    const saved = sessionStorage.getItem(KEY_STORAGE);
    if (saved) setApiKey(saved);
  }, []);

  const fetchList = useCallback(async (key: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/admin/conversations?limit=50`, {
        headers: { "X-Admin-Api-Key": key },
      });
      if (res.status === 401) throw new Error("Invalid admin key");
      if (!res.ok) throw new Error(`Failed to load (${res.status})`);
      setItems((await res.json()) as ConversationSummary[]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (apiKey) void fetchList(apiKey);
  }, [apiKey, fetchList]);

  async function openConversation(id: string) {
    if (!apiKey) return;
    setSelectedId(id);
    setDetail(null);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/admin/conversations/${id}`, {
        headers: { "X-Admin-Api-Key": apiKey },
      });
      if (!res.ok) throw new Error(`Failed to open chat (${res.status})`);
      setDetail((await res.json()) as ConversationDetail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to open chat");
    }
  }

  function onUnlock(e: FormEvent) {
    e.preventDefault();
    const key = keyInput.trim();
    if (!key) return;
    sessionStorage.setItem(KEY_STORAGE, key);
    setApiKey(key);
  }

  function onLock() {
    sessionStorage.removeItem(KEY_STORAGE);
    setApiKey(null);
    setKeyInput("");
    setItems([]);
    setDetail(null);
    setSelectedId(null);
  }

  if (!apiKey) {
    return (
      <div className="min-h-screen px-4 sm:px-8 py-16 max-w-md mx-auto">
        <p className="text-[0.7rem] uppercase tracking-[0.28em] text-[var(--muted)] mb-2">
          Private
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-[var(--ink)]">
          Inbox
        </h1>
        <p className="mt-2 text-[var(--muted)] leading-relaxed">
          Past visitor chats — only you can open this with your admin key.
        </p>
        <form onSubmit={onUnlock} className="mt-8 space-y-4">
          <label className="block space-y-1.5">
            <span className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
              Admin API key
            </span>
            <input
              type="password"
              autoComplete="current-password"
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
              className="w-full rounded-xl border border-[var(--line)] bg-[var(--panel)] px-3.5 py-2.5 outline-none focus:border-[var(--coral)]"
              placeholder="Your ADMIN_API_KEY"
            />
          </label>
          <button type="submit" className="btn-primary">
            Unlock inbox
          </button>
          {error ? <p className="text-sm text-[var(--danger)]">{error}</p> : null}
        </form>
        <Link href="/" className="mt-8 inline-block text-sm text-[var(--muted)] hover:text-[var(--ink)]">
          ← Back to site
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 h-16 flex items-center justify-between gap-3 px-4 sm:px-8 border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--bg)_90%,transparent)] backdrop-blur-md">
        <div>
          <div className="font-display font-semibold tracking-tight text-[var(--ink)]">Inbox</div>
          <div className="text-[0.65rem] uppercase tracking-[0.16em] text-[var(--muted)]">
            Private · visitors only you can see
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="btn-secondary !min-h-9 !px-3 text-sm"
            onClick={() => apiKey && fetchList(apiKey)}
            disabled={loading}
          >
            {loading ? "Refreshing…" : "Refresh"}
          </button>
          <button type="button" className="btn-secondary !min-h-9 !px-3 text-sm" onClick={onLock}>
            Lock
          </button>
          <Link href="/" className="text-sm text-[var(--muted)] hover:text-[var(--ink)] px-2">
            Site
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 sm:px-8 py-8 grid lg:grid-cols-[340px_1fr] gap-6">
        <section className="space-y-3">
          <h2 className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
            Conversations ({items.length})
          </h2>
          {error ? <p className="text-sm text-[var(--danger)]">{error}</p> : null}
          {items.length === 0 && !loading ? (
            <p className="text-sm text-[var(--muted)] leading-relaxed rounded-[1.1rem] border border-[var(--line)] bg-[var(--panel)] p-5">
              No chats yet. When someone talks to Ash, their questions and answers show up here.
            </p>
          ) : null}
          <div className="space-y-2 max-h-[70vh] overflow-y-auto pr-1">
            {items.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => openConversation(item.id)}
                className={[
                  "w-full text-left rounded-[1.1rem] border p-4 transition-colors",
                  selectedId === item.id
                    ? "border-[var(--coral)] bg-[var(--coral-soft)]"
                    : "border-[var(--line)] bg-[var(--panel)] hover:border-[rgba(232,90,58,0.35)]",
                ].join(" ")}
              >
                <div className="flex items-center justify-between gap-2 text-xs text-[var(--muted)]">
                  <span>{formatWhen(item.updated_at)}</span>
                  <span>{item.message_count} msgs</span>
                </div>
                <p className="mt-2 text-sm text-[var(--ink)] line-clamp-2 leading-relaxed">
                  {item.preview || "Empty conversation"}
                </p>
                {item.client_ip ? (
                  <p className="mt-2 text-[0.7rem] text-[var(--muted)]">IP {item.client_ip}</p>
                ) : null}
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] shadow-[var(--shadow)] min-h-[420px]">
          {!detail ? (
            <div className="h-full flex items-center justify-center p-8 text-[var(--muted)] text-sm">
              Select a conversation to read the full Q&amp;A.
            </div>
          ) : (
            <div className="flex flex-col h-full">
              <div className="px-5 py-4 border-b border-[var(--line)] space-y-1">
                <div className="font-semibold text-[var(--ink)]">Session {detail.session_id}</div>
                <div className="text-xs text-[var(--muted)]">
                  {formatWhen(detail.created_at)} → {formatWhen(detail.updated_at)}
                  {detail.client_ip ? ` · IP ${detail.client_ip}` : ""}
                </div>
              </div>
              <div className="p-5 space-y-4 overflow-y-auto max-h-[70vh]">
                {detail.messages.map((msg) => (
                  <article
                    key={msg.id}
                    className={
                      msg.role === "user"
                        ? "ml-8 rounded-2xl rounded-br-md bg-[var(--coral-soft)] px-4 py-3"
                        : "mr-4 rounded-2xl rounded-bl-md border border-[var(--line)] bg-white px-4 py-3"
                    }
                  >
                    <div className="text-[0.65rem] uppercase tracking-[0.16em] text-[var(--muted)] mb-1.5 flex justify-between gap-3">
                      <span>
                        {msg.role === "user" ? "Visitor" : "Ash"}
                        {msg.role === "assistant" && msg.grounded === false
                          ? " · needs review"
                          : ""}
                      </span>
                      <span>{formatWhen(msg.created_at)}</span>
                    </div>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed text-[var(--ink)]">
                      {msg.content}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
