'use client';
import { useState } from 'react';
import Link from 'next/link';
import { API_BASE } from '@/lib/api';
import { Markdown } from '@/components/Markdown';

export default function DocumentTool() {
  const [docType, setDocType] = useState('report');
  const [topic, setTopic] = useState('');
  const [requirements, setRequirements] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault(); if (!topic.trim()) return;
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/chat/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ message:`Create a ${docType}.\nTopic: ${topic}\nRequirements: ${requirements}\nUse clear headings, concise sections, and practical content.`, mode:'writer' }) });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || 'Request failed');
      setResult(data.response || '');
    } catch (e:any) { setError(e.message || 'Failed'); }
    finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen px-4 py-6"><div className="fixed inset-0 cyber-grid opacity-10 pointer-events-none"></div><div className="relative z-10 mx-auto max-w-6xl">
      <div className="mb-6 flex items-center gap-4"><Link href="/tools" className="text-gray-400 hover:text-cyan-300">← Tools</Link><h1 className="text-2xl font-bold text-cyan-400">📄 Document Creator</h1></div>
      <div className="grid gap-6 lg:grid-cols-2">
        <form onSubmit={submit} className="rounded-xl border border-cyan-500/20 bg-black/40 p-5 space-y-4">
          <label className="block text-sm">Type<select value={docType} onChange={e=>setDocType(e.target.value)} className="mt-1 w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2"><option>report</option><option>proposal</option><option>plan</option><option>brief</option><option>article</option><option>presentation outline</option></select></label>
          <label className="block text-sm">Topic<input value={topic} onChange={e=>setTopic(e.target.value)} className="mt-1 w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2" required placeholder="e.g. Q3 product launch plan" /></label>
          <label className="block text-sm">Requirements<textarea value={requirements} onChange={e=>setRequirements(e.target.value)} className="mt-1 h-40 w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2" placeholder="Audience, length, sections, constraints..." /></label>
          <button disabled={loading} className="rounded-lg bg-gradient-to-r from-cyan-500 to-violet-500 px-4 py-2 font-semibold disabled:opacity-50">{loading?'Creating…':'Create Document'}</button>
          {error && <div className="text-sm text-red-300">{error}</div>}
        </form>
        <div className="rounded-xl border border-cyan-500/20 bg-black/40 p-5 min-h-[420px]">{result ? <><div className="mb-3 flex justify-end"><button onClick={()=>navigator.clipboard?.writeText(result)} className="text-sm text-cyan-300">Copy</button></div><Markdown content={result} /></> : <div className="text-gray-500">Generated document appears here.</div>}</div>
      </div>
    </div></div>
  );
}
