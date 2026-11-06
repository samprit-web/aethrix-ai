import Link from 'next/link';

const tools = [
  { href: '/chat', icon: '💬', name: 'Chat', desc: 'Ask questions, brainstorm, analyze, and get help across tasks.' },
  { href: '/tools/email', icon: '✉️', name: 'Email', desc: 'Draft clear, professional emails with the right tone.' },
  { href: '/tools/document', icon: '📄', name: 'Documents', desc: 'Create structured reports, briefs, plans, and outlines.' },
  { href: '/tools/research', icon: '🔍', name: 'Research', desc: 'Explore topics with findings, implications, and next steps.' },
  { href: '/tools/meeting', icon: '📅', name: 'Meetings', desc: 'Plan agendas, scheduling details, and follow-ups.' },
  { href: '/tools/image', icon: '🎨', name: 'Images', desc: 'Generate image concepts and prompts.' },
];

export default function ToolsPage() {
  return (
    <div className="min-h-screen bg-[#212121] text-[#ececec]">
      <header className="flex h-14 items-center justify-between px-4 sm:px-6 border-b border-white/10">
        <Link href="/" className="text-lg font-semibold text-white">AETHRIX</Link>
        <Link href="/chat" className="rounded-full bg-white px-4 py-2 text-sm font-medium text-black hover:bg-gray-200">Open chat</Link>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <h1 className="text-3xl font-semibold text-white">Tools</h1>
        <p className="mt-2 text-[#b4b4b4]">Focused workflows built on the same assistant.</p>
        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tools.map(t => (
            <Link key={t.href} href={t.href} className="rounded-2xl border border-white/10 bg-[#171717] p-5 hover:bg-white/[0.04] transition">
              <div className="text-2xl">{t.icon}</div>
              <h2 className="mt-3 text-base font-semibold text-white">{t.name}</h2>
              <p className="mt-1 text-sm leading-6 text-[#b4b4b4]">{t.desc}</p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
