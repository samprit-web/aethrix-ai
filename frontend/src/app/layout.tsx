import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AETHRIX AI - Independent AI Platform",
  description: "Free-to-use alternative to ChatGPT, Gemini and Grok. AI chat, image generation, email drafting, meeting scheduling, document creation, research and productivity tools.",
  keywords: "AI, artificial intelligence, chatgpt alternative, free ai, open source ai",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
