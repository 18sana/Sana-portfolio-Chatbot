"use client";

import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost" | "nav";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  active?: boolean;
};

const styles: Record<Variant, string> = {
  primary:
    "bg-[var(--accent)] text-[var(--accent-fg)] px-6 py-3 text-sm font-semibold tracking-wide shadow-[0_0_0_0_rgba(198,241,53,0)] hover:shadow-[0_10px_30px_-12px_rgba(198,241,53,0.7)]",
  secondary:
    "border hairline bg-transparent px-6 py-3 text-sm font-medium hover:bg-[var(--panel)]",
  ghost:
    "text-xs uppercase tracking-wider text-[var(--muted)] hover:text-[var(--fg)] px-2 py-1",
  nav: "px-3 py-1.5 text-sm",
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = "primary", active = false, className = "", children, ...rest },
  ref,
) {
  const navActive = variant === "nav" && active
    ? "bg-[var(--accent)] text-[var(--accent-fg)]"
    : variant === "nav"
      ? "hover:bg-[var(--panel)]"
      : "";

  return (
    <button
      ref={ref}
      className={[
        "btn-press inline-flex items-center justify-center select-none",
        "transition-[transform,box-shadow,background-color,color,border-color] duration-[120ms] ease-out",
        "will-change-transform",
        "disabled:opacity-50 disabled:pointer-events-none",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]",
        styles[variant],
        navActive,
        className,
      ].join(" ")}
      {...rest}
    >
      {children}
    </button>
  );
});
