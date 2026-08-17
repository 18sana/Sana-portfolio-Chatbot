"use client";

type Props = {
  size?: number;
  className?: string;
};

/** Coral mark for Ash — used in header and brand moments. */
export function AshMark({ size = 28, className = "" }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <rect width="64" height="64" rx="16" fill="#E85A3A" />
      <path
        d="M32 14c-1.1 0-2.1.7-2.5 1.7L17.2 46.2c-.5 1.3.4 2.8 1.8 2.8h4.2c.9 0 1.7-.5 2-1.4L28.4 37h7.2l3.2 10.6c.3.9 1.1 1.4 2 1.4h4.2c1.4 0 2.3-1.5 1.8-2.8L34.5 15.7C34.1 14.7 33.1 14 32 14zm0 10.2L35.1 32h-6.2L32 24.2z"
        fill="#FFFFFF"
      />
    </svg>
  );
}
