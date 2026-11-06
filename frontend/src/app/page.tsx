'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#212121] text-[#ececec]">
      <header className="flex h-14 items-center justify-between px-4 sm:px-6">
        <Link href="/" className="text-lg font-semibold tracking-tight text-white">AETHRIX</Link>
        <div className="flex items-center gap-2">
          <Link href="/auth/login" className="rounded-full px-4 py-2 text-sm text-[#ececec] hover:bg-white/10">Log in</Link>
          <Link href="/chat" className="rounded-full bg-white px-4 py-2 text-sm font-medium text-black hover:bg-gray-200">Start chatting</Link>
        </div>
      </header>

      <main className="mx-auto flex min-h-[calc(100vh-56px)] max-w-3xl flex-col items-center justify-center px-4 pb-20 text-center">
        <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-white text-black">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-7 w-7"><path strokeLinecap="round" strokeLinejoin="round" d="M12 3l1.8 4.7L18 9.5l-4.2 1.8L12 16l-1.8-4.7L6 9.5l4.2-1.8z" /></svg>
        </div>
        <h1 className="mb-4 text-4xl font-semibold tracking-tight text-white sm:text-5xl">An intelligent AI assistant, built to be useful.</h1>
        <p className="mb-8 max-w-2xl text-lg text-[#b4b4b4]">Chat, write, code, research, plan, and create with a clean, focused interface. Free to use, designed for clarity and speed.</p>
        <div className="flex flex-wrap items-center justify-center gap-3">
          <Link href="/chat" className="rounded-full bg-white px-6 py-3 text-sm font-medium text-black hover:bg-gray-200">Open AETHRIX</Link>
          <Link href="/tools" className="rounded-full border border-white/15 px-6 py-3 text-sm font-medium text-[#ececec] hover:bg-white/5">Explore tools</Link>
        </div>
        <div className="mt-14 grid w-full gap-3 text-left sm:grid-cols-3">
          {[
            ['Intelligent chat', 'Streaming responses, conversation history, editing, and regeneration.'],
            ['Built-in tools', 'Email drafting, documents, research, meeting planning, and image workflows.'],
            ['Private by design', 'Independent architecture with configurable open-source model backends.'],
          ].map(([t,d]) => (
            <div key={t} className="rounded-2xl border border-white/10 bg-[#171717] p-4">
              <div className="mb-1 text-sm font-semibold text-white">{t}</div>
              <div className="text-sm leading-6 text-[#b4b4b4]">{d}</div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
