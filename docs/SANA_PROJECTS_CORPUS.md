# Sana Asiwal — Projects & Achievements (GitHub portfolio brief)

This document is the source of truth for Ash (Sana’s personal AI) about Sana Asiwal’s projects.
Speak only about Sana. Prefer intent and impact; mention stack only when useful.

GitHub profile: https://github.com/18sana

---

## Who Sana is (engineering focus)

Sana Asiwal builds full-stack products and AI agent systems: RAG platforms, multi-agent verification, MCP tool-calling agents, automation agents, and blockchain indexing/DeFi tooling. She works at Syvora as a Software Developer and ships open-source projects that recruiters can inspect on GitHub.

---

## Flagship AI / Agents projects

### RAG-Agent
**Intent:** Let enterprise AI assistants answer from a company’s own knowledge with trustworthy, source-backed replies — not hallucinations.
**What she built:** Multi-tenant RAG / policy Q&A platform in phased delivery: provider-agnostic LLM & embedding layer, tenant-isolated DB + chunking + vector store, retrieve → gate → grounded generate path, and Notion as a real external source for ingestion. Designed so swapping LLM providers is config-only.
**Why it matters:** Shows she can design production RAG with isolation, grounding, and extensible source adapters — the same class of problem companies hit when putting docs behind an assistant.
**Repo:** https://github.com/18sana/RAG-Agent

### Fact-Verification-Engine
**Intent:** Verify factual claims through structured debate instead of a single model “vibes check.”
**What she built:** Autonomous multi-agent system with Advocate, Skeptic, and Judge agents; hybrid retrieval + reranking; temporal knowledge graph (Neo4j); human escalation; adversarial testing; continuous Skeptic improvement via fine-tuning; evaluation on held-out data. Stack includes FastAPI, LangGraph, PostgreSQL/pgvector, Redis, Next.js dashboard, MLflow.
**Why it matters:** Demonstrates evaluation-minded AI engineering — debate, evidence, confidence, and human review — not just a chat demo.
**Repo:** https://github.com/18sana/Fact-Verification-Engine

### MCP Tool-Calling Agent
**Intent:** Show how enterprise agents can call tools safely under governance (access control, injection shields) with MCP + LangGraph.
**What she built:** Interactive enterprise console / simulator for MCP tool-calling agents orchestrated with LangGraph, Unity Catalog-style governance concepts, vector search exploration, and Databricks-oriented orchestration patterns. Includes production-oriented Python orchestrator scenarios (valid query vs blocked SQL injection).
**Why it matters:** Signals enterprise AI safety awareness: RBAC, SQLi shields, audit logs, governed tool registries.
**Repo:** https://github.com/18sana/mcp-tool-calling-agent

### RAG (Grounded Semantic AI Copilot)
**Intent:** Teach and demonstrate a full RAG path from upload → retrieval → grounded answer, including a from-scratch engine.
**What she built:** Dual-engine platform: custom RAG (recursive splitting, TF-IDF / NumPy cosine similarity) plus an enterprise-style layout (LangChain/Chroma-style reference). FastAPI backend + Next.js TypeScript/Tailwind dashboard with document, chat, and analytics views. Supports PDF/DOCX/TXT; OpenAI/Gemini when keys exist, offline mock fallback otherwise.
**Why it matters:** Shows depth — she understands RAG mechanics end-to-end, not only wrapping a library.
**Repo:** https://github.com/18sana/RAG

### Persistent Memory Assistant
**Intent:** Make assistants remember users across sessions so conversations stay personal and accurate over time.
**What she built:** AI assistant with persistent / cross-session memory for long-term context and personalized replies.
**Repo:** https://github.com/18sana/persistent-memory-assistant

### Social Media Automation Agent (Aether)
**Intent:** Automate social content operations without losing human control.
**What she built:** High-fidelity agent workspace demonstrating LangGraph-style state machines, tool calling (search/image), Slack-style HITL approval gates, cron scheduling, and revision loops before publish.
**Why it matters:** Shows product sense for agent UX — autonomy with mandatory human checkpoints.
**Repo:** https://github.com/18sana/social-media-automation-agent

### AI CI/CD Analyzer / FlowPilot (ai-cicd-analyzer-)
**Intent:** Help developers understand and fix CI/CD / pipeline failures faster (and ship solid product scaffolding).
**What she built:** Production-style Next.js 15 + React 19 + TypeScript app with Auth.js, Prisma/PostgreSQL, dashboard analytics, tasks, activity logs, Zod validation, Vitest, and CI scripts (lint/types/tests/build). Oriented toward developer productivity and pipeline health.
**Repo:** https://github.com/18sana/ai-cicd-analyzer-

### Tab Summarizer Extension
**Intent:** Turn noisy browser tabs into concise notes and optionally organize them into Notion.
**What she built:** Chrome extension that uses AI to summarize active tabs/pages and can dump organized data into Notion databases when configured.
**Repo:** https://github.com/18sana/Tab-summarizer-extension

### AI Foundations
**Intent:** Hands-on practice across modern AI building blocks.
**What she built:** Practical Python work covering prompting, RAG, tool calling, agents, memory, MCP, and evaluation/testing.
**Repo:** https://github.com/18sana/AI-Foundations

### Sana Portfolio Chatbot (this product)
**Intent:** Replace a static resume PDF with Ash — a grounded personal AI for recruiters (chat, JD fit, intro booking, private inbox).
**What she built:** FastAPI + hybrid RAG (pgvector + FTS), LangGraph chat with groundedness checks, JD match, Next.js portfolio UI, admin document ingest, Gemini providers, deployed with Vercel + Render + Supabase.
**Repo:** https://github.com/18sana/Sana-portfolio-Chatbot

---

## Product / full-stack projects

### SaveNServe (related: Sustainabite / food surplus)
**Intent:** Reduce food waste by connecting farmers, retailers, and NGOs to redistribute surplus food.
**What she built:** AI-powered food waste / redistribution platform with forecasting and matching concepts; related XRPL exploration for transparent donation tokenization, low-cost transfers, immutable records, and monitoring.
**Repo:** https://github.com/18sana/SaveNServe

### Hostel Management System
**Intent:** Digitize hostel operations.
**What she built:** System for student records, room allocation, attendance, fees, and admin operations.
**Repo:** https://github.com/18sana/Hostel_management_system

---

## Blockchain / systems projects

### Indexer / DAO indexing
**Intent:** Make on-chain DAO activity queryable for staking, locking, and governance.
**What she built:** Blockchain indexing that processes contract events (e.g. GovToken, Governance, Staking) into PostgreSQL for analytics-style queries. Related Indexer service for transaction/event processing and querying.
**Repos:** https://github.com/18sana/DAO · https://github.com/18sana/Indexer

### Exchange-Proxy
**Intent:** Support secure token swaps and routing in a decentralized exchange style architecture.
**What she built:** Smart-contract exchange proxy work (Solidity / Foundry toolchain).
**Repo:** https://github.com/18sana/Exchange-Proxy

### Wallet-Deriver
**Intent:** Derive and manage HD wallet addresses from seed phrases for blockchain workflows.
**Repo:** https://github.com/18sana/Wallet-Deriver

---

## How Ash should answer about projects

When a recruiter asks “what have you built?”, give a **short** answer: one lead sentence, then **at most 3** projects as single lines (**Name** — one sentence). Offer a deep dive. Only expand into bullets when they ask about a specific project. Do not invent metrics, employers, or features not listed here.
