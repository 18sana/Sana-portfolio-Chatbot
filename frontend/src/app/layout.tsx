import type { Metadata, Viewport } from "next";
import { DM_Sans, Space_Grotesk } from "next/font/google";
import "./globals.css";

const display = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "600", "700"],
});

const body = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Ash · Sana Asiwal",
  description:
    "Talk to Ash — Sana Asiwal’s AI. Grounded answers from real experience, JD fit checks, and intro booking.",
  applicationName: "Ash",
  authors: [{ name: "Sana Asiwal" }],
  icons: {
    icon: [{ url: "/ash-mark.svg", type: "image/svg+xml" }],
    apple: [{ url: "/ash-mark.svg", type: "image/svg+xml" }],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#e85a3a",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
