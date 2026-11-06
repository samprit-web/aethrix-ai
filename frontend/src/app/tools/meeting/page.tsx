'use client';
import { useState } from 'react';
import Link from 'next/link';
import { API_BASE } from '@/lib/api';
import { Markdown } from '@/components/Markdown';

export default function MeetingTool() {
  const [title, setTitle] = useState('');
  const [duration, setDuration] = useState(30);
  const [attendees, setAttendees] = useState('');
  const [preferences, setPreferences] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setLoading(true);
    const prompt = `Help plan a meeting.\nTitle: ${title}\nDuration: ${duration} minutes\nAttendees: ${attendees}\nPreferences/constraints: ${preferences}\nProvide: suggested agenda, best time considerations, preparation checklist, and follow-up actions.`;
    try {
      const res = await fetch(`${API_BASE}/chat/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ message: prompt, mode:'planner' }) });
      const data = await res.json().catch(()=>null);
      if (res.ok && data?.response) setResult(data.response);
      else {
        const r2 = await fetch(`${API_BASE}/meeting/schedule`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ title, duration, attendees: attendees.split(',').map(s=>s.trim()).filter(Boolean), preferences }) });
        const d2 = await r2.json(); setResult('```json\n'+JSON.stringify(d2,null,2)+'\n```');
      }
    } finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen px-4 py-6"><div className="fixed inset-0 cyber-grid opacity-10 pointer-events-none"></div><div className="relative z-10 mx-auto max-w-6xl">
      <div className="mb-6 flex items-center gap-4"><Link href="/tools" className="text-gray-400 hover:text-cyan-300">← Tools</Link><h1 className="text-2xl font-bold text-cyan-400">📅 Meeting Assistant</h1></div>
      <div className="grid gap-6 lg:grid-cols-2">
        <form onSubmit={submit} className="rounded-xl border border-cyan-500/20 bg-black/40 p-5 space-y-4">
          <input value={title} onChange={e=>setTitle(e.target.value)} className="w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2" placeholder="Meeting title" required />
          <input type="number" value={duration} onChange={e=>setDuration(Number(e.target.value)||30)} className="w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2" min={5} />
          <input value={attendees} onChange={e=>setAttendees(e.target.value)} className="w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2" placeholder="Attendees (comma separated)" />
          <textarea value={preferences} onChange={e=>setPreferences(e.target.value)} className="h-32 w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2" placeholder="Timezone, goals, constraints..." />
          <button disabled={loading} className="rounded-lg bg-gradient-to-r from-cyan-500 to-violet-500 px-4 py-2 font-semibold disabled:opacity-50">{loading?'Planning…':'Plan Meeting'}</button>
        </form>
        <div className="rounded-xl border border-cyan-500/20 bg-black/40 p-5 min-h-[420px]">{result ? <Markdown content={result} /> : <div className="text-gray-500">Meeting plan appears here.</div>}</div>
      </div>
    </div></div>
  );
}
