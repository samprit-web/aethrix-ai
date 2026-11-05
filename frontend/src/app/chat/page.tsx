'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { Markdown } from '@/components/Markdown';
import { API_BASE } from '@/lib/api';
import { Conversation, Message, MODELS, MODES, PROMPTS, loadConversations, newConversation, saveConversations, titleFrom, uid } from '@/lib/chat';

type ApiModel = { id: string; name: string; provider?: string };

async function* readSSE(res: Response): AsyncGenerator<any, void, unknown> {
  if (!res.body) return;
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = '';
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const parts = buf.split('\n\n');
    buf = parts.pop() || '';
    for (const part of parts) {
      const lines = part.split('\n').filter(l => l.startsWith('data:'));
      for (const line of lines) {
        const raw = line.replace(/^data:\s?/, '').trim();
        if (!raw || raw === '[DONE]') continue;
        try { yield JSON.parse(raw); } catch {}
      }
    }
  }
}

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState('');
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<ApiModel[]>(MODELS);
  const [customSystem, setCustomSystem] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [temperature, setTemperature] = useState(0.7);
  const [error, setError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const abortRef = useRef<AbortController | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const loaded = loadConversations();
    if (loaded.length) {
      setConversations(loaded);
      setActiveId(loaded[0].id);
    } else {
      const c = newConversation();
      setConversations([c]);
      setActiveId(c.id);
    }
    fetch(`${API_BASE}/chat/models`, { cache: 'no-store' })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.models?.length) setModels(d.models); })
      .catch(() => {});
  }, []);

  useEffect(() => { if (conversations.length) saveConversations(conversations); }, [conversations]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [conversations, activeId, loading]);

  const active = useMemo(() => conversations.find(c => c.id === activeId) || conversations[0], [conversations, activeId]);
  const mode = MODES.find(m => m.id === active?.mode) || MODES[0];

  function updateActive(updater: (c: Conversation) => Conversation) {
    setConversations(prev => prev.map(c => c.id === activeId ? updater(c) : c).sort((a,b)=>b.updatedAt-a.updatedAt));
  }

  function createChat() {
    const c = newConversation(active?.mode || 'assistant', active?.model || 'auto');
    setConversations(prev => [c, ...prev]);
    setActiveId(c.id);
    setInput('');
    setError('');
  }

  function deleteChat(id: string) {
    setConversations(prev => {
      const next = prev.filter(c => c.id !== id);
      const fallback = next[0] || newConversation();
      if (!next.length) next.push(fallback);
      if (activeId === id) setActiveId(next[0].id);
      return next;
    });
  }

  async function sendMessage(text?: string, opts?: { regenerate?: boolean }) {
    const content = (text ?? input).trim();
    if (!content || loading || !active) return;
    setError('');

    let baseMessages = active.messages;
    if (opts?.regenerate) {
      // remove last assistant response if present
      const copy = [...baseMessages];
      if (copy[copy.length - 1]?.role === 'assistant') copy.pop();
      baseMessages = copy;
    }

    const userMsg: Message = { id: uid(), role: 'user', content, createdAt: Date.now(), status: 'done' };
    const assistantId = uid();
    const assistantMsg: Message = { id: assistantId, role: 'assistant', content: '', createdAt: Date.now(), status: 'streaming' };
    const withUser = opts?.regenerate ? [...baseMessages, assistantMsg] : [...baseMessages, userMsg, assistantMsg];
    if (!opts?.regenerate) setInput('');

    updateActive(c => ({ ...c, messages: withUser, title: c.title === 'New chat' ? titleFrom(content) : c.title, updatedAt: Date.now() }));
    setLoading(true);

    const history = (opts?.regenerate ? baseMessages : [...baseMessages, userMsg])
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .slice(-20)
      .map(m => ({ role: m.role, content: m.content }));

    const payload = {
      message: content,
      model: active.model === 'auto' ? undefined : active.model,
      mode: active.mode,
      system: customSystem.trim() || undefined,
      temperature,
      history: history.slice(0, -1),
    };

    const controller = new AbortController();
    abortRef.current = controller;
    let full = '';
    try {
      const res = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) throw new Error(`Stream unavailable (${res.status})`);
      for await (const evt of readSSE(res)) {
        if (evt?.type === 'delta' && typeof evt.data === 'string') {
          full += evt.data;
          setConversations(prev => prev.map(c => c.id !== active.id ? c : ({
            ...c,
            updatedAt: Date.now(),
            messages: c.messages.map(m => m.id === assistantId ? { ...m, content: full } : m),
          })));
        }
      }
      if (!full) throw new Error('Empty response');
      setConversations(prev => prev.map(c => c.id !== active.id ? c : ({
        ...c, updatedAt: Date.now(), messages: c.messages.map(m => m.id === assistantId ? { ...m, content: full, status: 'done' } : m)
      })));
    } catch (e: any) {
      if (e?.name !== 'AbortError') {
        try {
          const res = await fetch(`${API_BASE}/chat/`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: controller.signal,
          });
          const data = await res.json();
          const text = data?.response || data?.detail || 'Request failed.';
          full = typeof text === 'string' ? text : JSON.stringify(text);
        } catch (e2: any) {
          if (e2?.name !== 'AbortError') {
            full = full || `I hit a connection issue reaching the AETHRIX backend (${API_BASE}). You can still use this workspace UI; start the backend or set NEXT_PUBLIC_API_BASE to enable live model responses.\n\nError: ${e2?.message || e?.message || 'unknown'}`;
            setError(e2?.message || e?.message || 'Connection error');
          }
        }
      }
      setConversations(prev => prev.map(c => c.id !== active.id ? c : ({
        ...c, updatedAt: Date.now(), messages: c.messages.map(m => m.id === assistantId ? { ...m, content: full || m.content || 'Stopped.', status: e?.name === 'AbortError' ? 'done' : (full ? 'done' : 'error') } : m)
      })));
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  }

  function stop() { abortRef.current?.abort(); }
  function regenerate() {
    if (!active) return;
    const lastUser = [...active.messages].reverse().find(m => m.role === 'user');
    if (lastUser) sendMessage(lastUser.content, { regenerate: true });
  }
  function copyText(text: string) { navigator.clipboard?.writeText(text); }
  function exportChat(format: 'json' | 'md') {
    if (!active) return;
    const content = format === 'json'
      ? JSON.stringify(active, null, 2)
      : `# ${active.title}\n\n` + active.messages.map(m => `## ${m.role}\n\n${m.content}`).join('\n\n');
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${active.title.replace(/[^a-z0-9]+/gi,'-').toLowerCase() || 'chat'}.${format === 'json' ? 'json' : 'md'}`;
    a.click();
  }

  if (!active) return <div className="min-h-screen bg-black text-white p-8">Loading…</div>;

  return (
    <div className="min-h-screen bg-[#02040a] text-white">
      <div className="fixed inset-0 cyber-grid opacity-[0.07] pointer-events-none"></div>
      <div className="relative z-10 flex h-screen">
        <aside className={`${sidebarOpen ? 'w-72' : 'w-0 md:w-16'} transition-all duration-200 border-r border-cyan-500/15 bg-black/40 backdrop-blur overflow-hidden flex flex-col`}>
          <div className="p-3 border-b border-cyan-500/10 flex items-center gap-2">
            <button onClick={createChat} className="flex-1 rounded-lg bg-gradient-to-r from-cyan-500/90 to-violet-500/90 px-3 py-2 text-sm font-semibold hover:opacity-95">+ New chat</button>
            <button onClick={() => setSidebarOpen(v=>!v)} className="rounded-lg border border-cyan-500/20 px-2 py-2 text-sm text-gray-300 hover:text-white">{sidebarOpen ? '«' : '»'}</button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {conversations.map(c => (
              <div key={c.id} className={`group rounded-lg px-2 py-2 text-sm cursor-pointer border ${c.id===activeId?'border-cyan-500/30 bg-cyan-500/10':'border-transparent hover:bg-white/5'}`} onClick={()=>setActiveId(c.id)}>
                <div className="flex items-center gap-2">
                  <div className="min-w-0 flex-1 truncate">{c.title}</div>
                  {sidebarOpen && <button onClick={(e)=>{e.stopPropagation(); deleteChat(c.id);}} className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-300 px-1">×</button>}
                </div>
                {sidebarOpen && <div className="mt-0.5 text-[11px] text-gray-500 truncate">{MODELS.find(m=>m.id===c.mode)?.name || c.mode} · {c.messages.length} msgs</div>}
              </div>
            ))}
          </div>
          <div className="p-3 border-t border-cyan-500/10 text-xs text-gray-400 space-y-2">
            <div className="flex gap-2"><Link href="/" className="hover:text-cyan-300">Home</Link><span>·</span><span className="text-green-400">Intelligent mode</span></div>
            <div className="text-[11px] text-gray-500">API: {API_BASE}</div>
          </div>
        </aside>

        <main className="flex-1 flex flex-col min-w-0">
          <header className="border-b border-cyan-500/15 bg-black/30 backdrop-blur px-4 py-3 flex items-center gap-3 flex-wrap">
            <button className="md:hidden rounded border border-cyan-500/20 px-2 py-1" onClick={()=>setSidebarOpen(v=>!v)}>Menu</button>
            <div className="font-semibold text-cyan-300">AETHRIX AI</div>
            <select value={active.mode} onChange={e=>updateActive(c=>({...c, mode:e.target.value, updatedAt:Date.now()}))} className="rounded-lg border border-cyan-500/20 bg-black/50 px-2 py-1.5 text-sm">
              {MODES.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
            </select>
            <select value={active.model} onChange={e=>updateActive(c=>({...c, model:e.target.value, updatedAt:Date.now()}))} className="rounded-lg border border-cyan-500/20 bg-black/50 px-2 py-1.5 text-sm max-w-[220px]">
              {models.map(m => <option key={m.id} value={m.id}>{m.name || m.id}</option>)}
            </select>
            <div className="ml-auto flex items-center gap-2 text-sm">
              <button onClick={()=>setShowSettings(v=>!v)} className="rounded-lg border border-cyan-500/20 px-2 py-1.5 text-gray-300 hover:text-white">Settings</button>
              <button onClick={()=>exportChat('md')} className="rounded-lg border border-cyan-500/20 px-2 py-1.5 text-gray-300 hover:text-white">Export</button>
              <button onClick={()=>updateActive(c=>({...c,messages:[newConversation(c.mode,c.model).messages[0]],updatedAt:Date.now(),title:'New chat'}))} className="rounded-lg border border-cyan-500/20 px-2 py-1.5 text-gray-300 hover:text-white">Clear</button>
            </div>
          </header>

          {showSettings && (
            <div className="border-b border-cyan-500/10 bg-black/30 px-4 py-3 text-sm space-y-3">
              <div className="flex flex-wrap gap-4 items-center">
                <label className="flex items-center gap-2">Temperature <input type="range" min="0" max="1" step="0.1" value={temperature} onChange={e=>setTemperature(Number(e.target.value))} /><span className="text-gray-400 w-8">{temperature}</span></label>
                <div className="text-gray-400">Mode behavior: {mode.prompt}</div>
              </div>
              <label className="block">Custom system instructions (optional)
                <textarea value={customSystem} onChange={e=>setCustomSystem(e.target.value)} placeholder="Add extra instructions for this session..." className="mt-1 w-full rounded-lg border border-cyan-500/20 bg-black/50 p-2 h-20" />
              </label>
            </div>
          )}

          <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="mx-auto max-w-4xl space-y-5">
              {active.messages.length <= 1 && (
                <div className="mb-6 grid gap-2 sm:grid-cols-2">
                  {PROMPTS.map(p => (
                    <button key={p} onClick={()=>{setInput(p); textareaRef.current?.focus();}} className="rounded-xl border border-cyan-500/15 bg-white/[0.02] p-3 text-left text-sm text-gray-300 hover:border-cyan-500/30 hover:bg-cyan-500/5">
                      {p}
                    </button>
                  ))}
                </div>
              )}
              {active.messages.map((m) => (
                <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[92%] md:max-w-[80%] rounded-2xl px-4 py-3 ${m.role === 'user' ? 'bg-gradient-to-r from-cyan-600 to-violet-600 text-white' : 'border border-cyan-500/15 bg-white/[0.03]'}`}>
                    <div className="mb-1 flex items-center gap-2 text-[11px] uppercase tracking-wide opacity-70">
                      <span>{m.role === 'user' ? 'You' : 'AETHRIX'}</span>
                      {m.status === 'streaming' && <span className="text-cyan-300">thinking…</span>}
                    </div>
                    {m.role === 'assistant' ? <Markdown content={m.content || (m.status==='streaming' ? '…' : '')} /> : <div className="whitespace-pre-wrap leading-7">{m.content}</div>}
                    <div className="mt-2 flex gap-2 text-[11px] text-gray-400">
                      <button onClick={()=>copyText(m.content)} className="hover:text-cyan-300">Copy</button>
                      {m.role === 'user' && <button onClick={()=>{setInput(m.content); textareaRef.current?.focus();}} className="hover:text-cyan-300">Edit</button>}
                    </div>
                  </div>
                </div>
              ))}
              {error && <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</div>}
              <div ref={endRef} />
            </div>
          </div>

          <div className="border-t border-cyan-500/15 bg-black/40 p-4">
            <div className="mx-auto max-w-4xl">
              <div className="mb-2 flex items-center gap-2 text-xs text-gray-400">
                <span>{mode.name} mode</span><span>·</span><span>{active.model}</span><span>·</span><span>Markdown & code supported</span>
                {loading ? <button onClick={stop} className="ml-auto rounded border border-red-400/30 px-2 py-1 text-red-200 hover:bg-red-500/10">Stop</button> : <button onClick={regenerate} className="ml-auto rounded border border-cyan-500/20 px-2 py-1 hover:bg-cyan-500/10">Regenerate</button>}
              </div>
              <form onSubmit={(e)=>{e.preventDefault(); sendMessage();}} className="rounded-2xl border border-cyan-500/20 bg-black/50 p-2 shadow-[0_0_0_1px_rgba(0,255,255,0.03)] focus-within:border-cyan-400/40">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={e=>setInput(e.target.value)}
                  onKeyDown={e=>{ if (e.key==='Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  placeholder="Message AETHRIX… (Enter to send, Shift+Enter for newline)"
                  className="max-h-48 min-h-[52px] w-full resize-y bg-transparent px-3 py-2 outline-none placeholder:text-gray-500"
                  disabled={loading}
                />
                <div className="flex items-center justify-between px-2 pb-1">
                  <div className="flex gap-2 text-xs text-gray-500">
                    <button type="button" onClick={()=>setInput(v=>v + (v?"\n\n":"") + "Use this context:\n")} className="rounded px-2 py-1 hover:bg-white/5">+ Context</button>
                    <button type="button" onClick={()=>setInput(v=>v + (v?"\n\n":"") + "Please respond with: 1) answer, 2) assumptions, 3) next steps.")} className="rounded px-2 py-1 hover:bg-white/5">+ Structure</button>
                  </div>
                  <button type="submit" disabled={loading || !input.trim()} className="rounded-xl bg-gradient-to-r from-cyan-500 to-violet-500 px-4 py-2 font-semibold disabled:opacity-40">Send</button>
                </div>
              </form>
              <div className="mt-2 text-center text-[11px] text-gray-500">AETHRIX can make mistakes. Verify important information. Configure a local model backend for full private inference.</div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
