'use client';
import { useState } from 'react';
import Link from 'next/link';
import { API_BASE } from '@/lib/api';
import { Markdown } from '@/components/Markdown';

export default function ResearchTool() {
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState('standard');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault(); if (!query.trim()) return;
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/research/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ query, depth }) });
      const data = await res.json().catch(()=>null);
      if (res.ok && data?.content) setResult(data.content);
      else {
        const r2 = await fetch(`${API_BASE}/chat/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ message:`Research (${depth}) this topic and provide key findings, implications, uncertainties, and next steps:\n${query}`, mode:'research' }) });
        const d2 = await r2.json(); if (!r2.ok) throw new Error(d2?.detail || 'Request failed'); setResult(d2.response||'');
      }
    } catch (e:any) { setError(e.message || 'Failed'); }
    finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen px-4 py-6"><div className="fixed inset-0 cyber-grid opacity-10 pointer-events-none"></div><div className="relative z-10 mx-auto max-w-6xl">
      <div className="mb-6 flex items-center gap-4"><Link href="/tools" className="text-gray-400 hover:text-cyan-300">← Tools</Link><h1 className="text-2xl font-bold text-cyan-400">🔍 Research Assistant</h1></div>
      <form onSubmit={submit} className="mb-6 rounded-xl border border-cyan-500/20 bg-black/40 p-5 space-y-4">
        <label className="block text-sm">Research question<textarea value={query} onChange={e=>setQuery(e.target.value)} className="mt-1 h-28 w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2" required /></label>
        <div className="flex gap-3 items-center"><select value={depth} onChange={e=>setDepth(e.target.value)} className="rounded-lg border border-cyan-500/20 bg-black/50 p-2 text-sm"><option value="quick">Quick</option><option value="standard">Standard</option><option value="deep">Deep</option></select><button disabled={loading} className="rounded-lg bg-gradient-to-r from-cyan-500 to-violet-500 px-4 py-2 font-semibold disabled:opacity-50">{loading?'Researching…':'Run Research'}</button></div>
        {error && <div className="text-sm text-red-300">{error}</div>}
      </form>
      <div className="rounded-xl border border-cyan-500/20 bg-black/40 p-5 min-h-[320px]">{result ? <Markdown content={result} /> : <div className="text-gray-500">Research results appear here.</div>}</div>
    </div></div>
  );
}
