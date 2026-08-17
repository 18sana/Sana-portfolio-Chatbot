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
        "Open-source engine so enterprise AI assistants can answer from a company’s own knowledge — with trustworthy, source-backed replies across teams and document workspaces, not hallucinations.",
      githubUrl: "https://github.com/18sana/RAG-Agent",
      tags: ["RAG", "Agents", "Python", "Enterprise"],
    },
    {
      name: "SaveNServe",
      description:
        "AI-powered food waste platform connecting farmers, retailers, and NGOs to redistribute surplus food with forecasting and real-time matching.",
      githubUrl: "https://github.com/18sana/SaveNServe",
      tags: ["AI", "Full-stack", "Socket.IO"],
    },
    {
      name: "Fact-Verification-Engine",
      description:
        "Multi-agent fact-checking system with Advocate, Skeptic, and Judge agents, RAG evidence, human review, and evaluation harnesses.",
      githubUrl: "https://github.com/18sana/Fact-Verification-Engine",
      tags: ["Agents", "RAG", "Evaluation"],
    },
    {
      name: "MCP Tool-Calling Agent",
      description:
        "Enterprise AI agent using Model Context Protocol for secure tool calling, governed data access, and LangGraph workflows.",
      githubUrl: "https://github.com/18sana/mcp-tool-calling-agent",
      tags: ["MCP", "LangGraph", "Enterprise"],
    },
    {
      name: "Indexer",
      description:
        "Blockchain indexing service for processing, storing, and querying on-chain transactions and events.",
      githubUrl: "https://github.com/18sana/Indexer",
      tags: ["Blockchain", "PostgreSQL"],
    },
    {
      name: "Exchange-Proxy",
      description:
        "Smart-contract exchange proxy for secure token swaps, routing, and decentralized trading operations.",
      githubUrl: "https://github.com/18sana/Exchange-Proxy",
      tags: ["Smart contracts", "DeFi"],
    },
    {
      name: "Persistent Memory Assistant",
      description:
        "AI assistant with cross-session memory for personalized conversations and long-term context.",
      githubUrl: "https://github.com/18sana/persistent-memory-assistant",
      tags: ["AI", "Memory"],
    },
    {
      name: "Social Media Automation Agent",
      description:
        "Autonomous content agent that generates, reviews, schedules, and publishes with human-in-the-loop workflows.",
      githubUrl: "https://github.com/18sana/social-media-automation-agent",
      tags: ["Agents", "Automation"],
    },
  ] satisfies Project[],
} as const;
