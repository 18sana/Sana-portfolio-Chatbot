export type Project = {
  name: string;
  description: string;
  githubUrl: string;
  tags?: string[];
};

export type Certification = {
  name: string;
  detail: string;
  /** Credential / certificate page or PDF URL — opens in a new tab */
  url: string;
};

export const profile = {
  fullName: "Sana Asiwal",
  /** Personal AI name — derived from Asiwal */
  aiName: "Ash",
  aiTagline: "Sana’s AI — knows the work cold.",
  title: "Software Developer",
  location: "Indore, India",
  timezone: "Asia/Kolkata (IST)",
  company: "Syvora",
  email: "sanaasiwal18@gmail.com",
  resumeUrl:
    "https://docs.google.com/document/d/1cMi2WvQHBAM_f0CgOG_ZZmTJn54ZLId4wdVh4FrOx6M/edit?usp=sharing",
  githubUrl: "https://github.com/18sana",
  linkedinUrl: "https://www.linkedin.com/in/sana-asiwal18",
  /**
   * Optional: Cal.com / Calendly / Google Appointment link.
   * Leave empty to use the Meet form → email briefing flow.
   */
  bookingUrl: "",
  certifications: [
    {
      name: "System Design",
      detail:
        "Grokking Modern System Design Interview — Educative. Distributed systems & interview-ready design practice.",
      url: "https://www.educative.io/verify-certificate/KOnpGJIMRWnmgGzjohnr2r99EO4WFB",
    },
    {
      name: "MERN Stack",
      detail:
        "MERN Stack Application Development — TechSaksham (Microsoft & SAP aligned).",
      url: "https://techsaksham.org/verify-certificate-v2/TSPIN25_606495",
    },
  ] satisfies Certification[],
  projects: [
    {
      name: "RAG-Agent",
      description:
        "Built so companies can trust AI assistants with their own documents — multi-tenant RAG with grounded answers, provider-agnostic LLMs, and real source ingestion (starting with Notion).",
      githubUrl: "https://github.com/18sana/RAG-Agent",
      tags: ["RAG", "Agents", "Python", "Enterprise"],
    },
    {
      name: "Fact-Verification-Engine",
      description:
        "Verifies claims through Advocate / Skeptic / Judge debate, hybrid retrieval, knowledge graphs, human review, and evaluation — evidence over vibes.",
      githubUrl: "https://github.com/18sana/Fact-Verification-Engine",
      tags: ["Agents", "RAG", "Evaluation", "LangGraph"],
    },
    {
      name: "MCP Tool-Calling Agent",
      description:
        "Enterprise MCP + LangGraph agent console focused on governed tool calling — access control, injection shields, and auditable agent workflows.",
      githubUrl: "https://github.com/18sana/mcp-tool-calling-agent",
      tags: ["MCP", "LangGraph", "Governance"],
    },
    {
      name: "RAG Copilot",
      description:
        "End-to-end grounded RAG copilot with a from-scratch retrieval engine and a FastAPI + Next.js dashboard — upload docs, retrieve, answer with sources.",
      githubUrl: "https://github.com/18sana/RAG",
      tags: ["RAG", "FastAPI", "Next.js"],
    },
    {
      name: "SaveNServe",
      description:
        "AI-powered food waste platform connecting farmers, retailers, and NGOs to redistribute surplus food — impact-focused full-stack product work.",
      githubUrl: "https://github.com/18sana/SaveNServe",
      tags: ["Full-stack", "AI", "Impact"],
    },
    {
      name: "Social Media Automation Agent",
      description:
        "Autonomous content agent with LangGraph-style workflows, tool calling, Slack-style human approval, and scheduling before anything goes live.",
      githubUrl: "https://github.com/18sana/social-media-automation-agent",
      tags: ["Agents", "HITL", "Automation"],
    },
    {
      name: "Persistent Memory Assistant",
      description:
        "Assistant that keeps user context across sessions so conversations stay personal and accurate over time.",
      githubUrl: "https://github.com/18sana/persistent-memory-assistant",
      tags: ["AI", "Memory"],
    },
    {
      name: "AI CI/CD Analyzer",
      description:
        "Developer productivity platform around pipeline health and solid product scaffolding — Next.js, Auth, Prisma/Postgres, tests, and CI discipline.",
      githubUrl: "https://github.com/18sana/ai-cicd-analyzer-",
      tags: ["Next.js", "CI/CD", "TypeScript"],
    },
    {
      name: "DAO / Indexer",
      description:
        "Indexes on-chain DAO events into PostgreSQL so staking, locking, and governance activity become queryable — blockchain data engineering.",
      githubUrl: "https://github.com/18sana/DAO",
      tags: ["Blockchain", "PostgreSQL", "Indexing"],
    },
    {
      name: "Exchange-Proxy",
      description:
        "Smart-contract exchange proxy for secure token swaps and routing in decentralized trading flows.",
      githubUrl: "https://github.com/18sana/Exchange-Proxy",
      tags: ["Solidity", "DeFi"],
    },
    {
      name: "Tab Summarizer",
      description:
        "Chrome extension that summarizes tabs with AI and can organize insights into Notion databases.",
      githubUrl: "https://github.com/18sana/Tab-summarizer-extension",
      tags: ["Extension", "AI", "Notion"],
    },
    {
      name: "Ash · Portfolio Chatbot",
      description:
        "This site — personal AI for recruiters with grounded chat, JD fit, intro booking, and private inbox over Sana’s real documents.",
      githubUrl: "https://github.com/18sana/Sana-portfolio-Chatbot",
      tags: ["RAG", "FastAPI", "Next.js"],
    },
  ] satisfies Project[],
} as const;
