"use client";

import { motion, useReducedMotion } from "motion/react";
import { profile } from "@/data/profile";

export function PortfolioPanel() {
  const reduced = useReducedMotion();

  return (
    <div className="space-y-8 sm:space-y-10">
      <div>
        <h2 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-[var(--ink)]">
          Resume & work
        </h2>
        <p className="mt-2 text-sm sm:text-base text-[var(--muted)] max-w-xl leading-relaxed">
          Open my resume, profiles, certifications, and GitHub projects in one place.
        </p>
      </div>

      {/* Quick links */}
      <div className="flex flex-col sm:flex-row flex-wrap gap-3">
        <a
          href={profile.resumeUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary w-full sm:w-auto"
        >
          See resume
          <span aria-hidden>↗</span>
        </a>
        <div className="grid grid-cols-2 sm:flex gap-3">
          <a
            href={profile.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary w-full sm:w-auto"
          >
            GitHub
          </a>
          <a
            href={profile.linkedinUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary w-full sm:w-auto"
          >
            LinkedIn
          </a>
        </div>
      </div>

      {/* Certifications */}
      <section>
        <h3 className="text-xs uppercase tracking-[0.2em] text-[var(--muted)] mb-4">
          Certifications
        </h3>
        <div className="grid sm:grid-cols-2 gap-3">
          {profile.certifications.map((cert, i) => {
            const content = (
              <>
                <div className="flex items-start justify-between gap-3">
                  <h4 className="font-semibold text-[var(--ink)]">{cert.name}</h4>
                  {cert.url ? (
                    <span className="shrink-0 text-sm font-semibold text-[var(--coral)]">
                      Open ↗
                    </span>
                  ) : null}
                </div>
                <p className="mt-2 text-sm text-[var(--muted)] leading-relaxed">{cert.detail}</p>
              </>
            );

            const className =
              "block rounded-[1.1rem] border border-[var(--line)] bg-[var(--panel)] p-4 sm:p-5 shadow-sm transition-colors hover:border-[rgba(232,90,58,0.4)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--coral)]";

            return cert.url ? (
              <motion.a
                key={cert.name}
                href={cert.url}
                target="_blank"
                rel="noopener noreferrer"
                className={className}
                initial={reduced ? false : { opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06, duration: 0.35 }}
              >
                {content}
              </motion.a>
            ) : (
              <motion.article
                key={cert.name}
                className={className}
                initial={reduced ? false : { opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06, duration: 0.35 }}
              >
                {content}
              </motion.article>
            );
          })}
        </div>
      </section>

      {/* Projects */}
      <section>
        <div className="flex items-end justify-between gap-4 mb-4">
          <h3 className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">
            GitHub projects
          </h3>
          <a
            href={profile.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-semibold text-[var(--coral)] hover:underline"
          >
            View all →
          </a>
        </div>
        <div className="space-y-3">
          {profile.projects.map((project, i) => (
            <motion.article
              key={project.name}
              className="rounded-[1.1rem] border border-[var(--line)] bg-[var(--panel)] p-4 sm:p-5 shadow-sm hover:border-[rgba(232,90,58,0.35)] transition-colors"
              initial={reduced ? false : { opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 + i * 0.04, duration: 0.35 }}
            >
              <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-start sm:justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <h4 className="font-display text-base sm:text-lg font-semibold tracking-tight text-[var(--ink)]">
                    {project.name}
                  </h4>
                  <p className="mt-2 text-sm text-[var(--muted)] leading-relaxed">
                    {project.description}
                  </p>
                  {project.tags ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {project.tags.map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full bg-[var(--bg)] border border-[var(--line)] px-2.5 py-1 text-xs text-[var(--ink-soft)]"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
                <a
                  href={project.githubUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="shrink-0 inline-flex items-center justify-center gap-1.5 rounded-full border border-[var(--line-strong)] bg-white px-3.5 py-2 text-sm font-semibold text-[var(--ink)] hover:border-[var(--coral)] hover:text-[var(--coral)] transition-colors w-full sm:w-auto"
                >
                  GitHub
                  <span aria-hidden>↗</span>
                </a>
              </div>
            </motion.article>
          ))}
        </div>
      </section>
    </div>
  );
}
