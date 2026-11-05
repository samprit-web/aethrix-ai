import Link from 'next/link';

const tools = [
  { href: '/chat', icon: '💬', name: 'AI Chat', desc: 'Multi-mode intelligent chat with streaming, history, export, and model controls.' },
  { href: '/tools/image', icon: '🎨', name: 'Image Generation', desc: 'Create visual concepts and image prompts through the image API.' },
  { href: '/tools/email', icon: '✉️', name: 'Email Drafting', desc: 'Generate polished emails with purpose, tone, and context.' },
  { href: '/tools/document', icon: '📄', name: 'Document Creator', desc: 'Draft reports, plans, briefs, and structured documents.' },
  { href: '/tools/research', icon: '🔍', name: 'Research Assistant', desc: 'Analyze topics with findings, implications, and next steps.' },
  { href: '/tools/meeting', icon: '📅', name: 'Meeting Assistant', desc: 'Plan meetings, agendas, and scheduling suggestions.' },
];

export default function ToolsPage() {
  return (
    <div className="min-h-screen px-4 py-10">
      <div className="fixed inset-0 cyber-grid opacity-10 pointer-events-none"></div>
      <div className="relative z-10 mx-auto max-w-6xl">
        <div className="mb-8 flex items-center justify-between"><Link href="/" className="text-cyan-400 hover:text-cyan-300">← Home</Link><Link href="/chat" className="rounded-lg bg-gradient-to-r from-cyan-500 to-violet-500 px-4 py-2 font-semibold">Open Chat</Link></div>
        <h1 className="mb-3 text-4xl font-bold glow-text text-cyan-400">AETHRIX Tools</h1>
        <p className="mb-8 text-gray-400">A unified suite for conversation, creation, research, and productivity.</p>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {tools.map(t => (
            <Link key={t.href} href={t.href} className="rounded-xl border border-cyan-500/20 bg-black/40 p-5 hover:border-cyan-400/40 hover:bg-cyan-500/5 transition">
              <div className="mb-3 text-3xl">{t.icon}</div>
              <h2 className="mb-2 text-xl font-semibold text-cyan-200">{t.name}</h2>
              <p className="text-sm leading-6 text-gray-400">{t.desc}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
