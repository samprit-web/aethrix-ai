'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
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
      for (const line of part.split('\n').filter(l => l.startsWith('data:'))) {
        const raw = line.replace(/^data:\s?/, '').trim();
        if (!raw || raw === '[DONE]') continue;
        try { yield JSON.parse(raw); } catch {}
      }
    }
  }
}

const Icon = ({ path, className = 'h-5 w-5' }: { path: string; className?: string }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className}><path d={path} /></svg>
);
const icons = {
  plus: 'M12 5v14M5 12h14',
  menu: 'M4 7h16M4 12h16M4 17h16',
  side: 'M4 5h16v14H4zM9 5v14',
  send: 'M5 12h13M13 6l6 6-6 6',
  stop: 'M7 7h10v10H7z',
  copy: 'M9 9h10v10H9zM5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1',
  edit: 'M12 20h9M16.5 3.5a2.1 2.1 0 1 1 3 3L7 19l-4 1 1-4Z',
  refresh: 'M21 12a9 9 0 1 1-2.64-6.36M21 3v6h-6',
  trash: 'M3 6h18M8 6V4h8v2m-7 4v7m4-7v7M6 6l1 14h10l1-14',
  more: 'M5 12h.01M12 12h.01M19 12h.01',
  close: 'M6 6l12 12M18 6 6 18',
  spark: 'M12 3l1.8 4.7L18 9.5l-4.2 1.8L12 16l-1.8-4.7L6 9.5l4.2-1.8z',
  user: 'M20 21a8 8 0 0 0-16 0M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
};

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState('');
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<ApiModel[]>(MODELS);
  const [error, setError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileSidebar, setMobileSidebar] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const abortRef = useRef<AbortController | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const loaded = loadConversations();
    if (loaded.length) { setConversations(loaded); setActiveId(loaded[0].id); }
    else { const c = newConversation(); setConversations([c]); setActiveId(c.id); }
    fetch(`${API_BASE}/chat/models`, { cache: 'no-store' }).then(r => r.ok ? r.json() : null).then(d => {
      if (d?.models?.length) setModels(d.models.map((m: any) => ({ id: m.id, name: m.name || m.id, provider: m.provider })));
    }).catch(() => {});
  }, []);

  useEffect(() => { if (conversations.length) saveConversations(conversations); }, [conversations]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [conversations, activeId, loading]);

  const active = useMemo(() => conversations.find(c => c.id === activeId) || conversations[0], [conversations, activeId]);
  const mode = MODES.find(m => m.id === active?.mode) || MODES[0];

  function updateActive(updater: (c: Conversation) => Conversation) {
    setConversations(prev => prev.map(c => c.id === activeId ? updater(c) : c).sort((a, b) => b.updatedAt - a.updatedAt));
  }
  function createChat() {
    const c = newConversation(active?.mode || 'assistant', active?.model || 'auto');
    setConversations(prev => [c, ...prev]); setActiveId(c.id); setInput(''); setError(''); setMobileSidebar(false);
  }
  function deleteChat(id: string) {
    setConversations(prev => {
      const next = prev.filter(c => c.id !== id);
      if (!next.length) next.push(newConversation());
      if (activeId === id) setActiveId(next[0].id);
      return next;
    });
  }
  function copyText(text: string) { navigator.clipboard?.writeText(text).catch(() => {}); }
  function stop() { abortRef.current?.abort(); }

  async function sendMessage(text?: string, opts?: { regenerate?: boolean; fromIndex?: number }) {
    const content = (text ?? input).trim();
    if (!content || loading || !active) return;
    setError('');
    let base = active.messages;
    if (opts?.regenerate) {
      base = [...base]; if (base[base.length - 1]?.role === 'assistant') base.pop();
    } else if (typeof opts?.fromIndex === 'number') {
      base = base.slice(0, opts.fromIndex);
    }
    const userMsg: Message = { id: uid(), role: 'user', content, createdAt: Date.now(), status: 'done' };
    const assistantId = uid();
    const withUser = [...base, userMsg, { id: assistantId, role: 'assistant', content: '', createdAt: Date.now(), status: 'streaming' as const }];
    if (!opts?.regenerate && typeof opts?.fromIndex !== 'number') setInput('');
    setEditingId(null);
    updateActive(c => ({ ...c, messages: withUser, title: c.title === 'New chat' ? titleFrom(content) : c.title, updatedAt: Date.now() }));
    setLoading(true);

    const history = withUser.filter(m => m.role !== 'system' && m.status !== 'streaming').slice(-24).map(m => ({ role: m.role, content: m.content }));
    const payload = { message: content, model: active.model === 'auto' ? undefined : active.model, mode: active.mode, temperature: 0.7, history: history.slice(0, -1) };
    const controller = new AbortController(); abortRef.current = controller;
    let full = '';
    const patch = (textVal: string, status: Message['status']) => setConversations(prev => prev.map(c => c.id !== active.id ? c : ({ ...c, updatedAt: Date.now(), messages: c.messages.map(m => m.id === assistantId ? { ...m, content: textVal, status } : m) })));
    try {
      const res = await fetch(`${API_BASE}/chat/stream`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: controller.signal });
      if (!res.ok || !res.body) throw new Error(`Request failed (${res.status})`);
      for await (const evt of readSSE(res)) { if (evt?.type === 'delta' && typeof evt.data === 'string') { full += evt.data; patch(full, 'streaming'); } }
      if (!full) throw new Error('empty');
      patch(full, 'done');
    } catch (e: any) {
      if (e?.name !== 'AbortError') {
        try {
          const r2 = await fetch(`${API_BASE}/chat/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: controller.signal });
          const d2 = await r2.json().catch(() => ({}));
          full = typeof d2?.response === 'string' ? d2.response : (d2?.detail || full);
        } catch (e2: any) {
          if (e2?.name !== 'AbortError') { setError('Unable to reach the AI service. Check backend/API configuration.'); full = full || 'I couldn’t reach the AI service right now. Please try again, or verify the backend is running and `NEXT_PUBLIC_API_BASE` is configured.'; }
        }
      }
      patch(full || 'Stopped.', full ? 'done' : (e?.name === 'AbortError' ? 'done' : 'error'));
    } finally { setLoading(false); abortRef.current = null; }
  }

  function regenerate() {
    if (!active) return;
    const lastUser = [...active.messages].reverse().find(m => m.role === 'user');
    if (lastUser) sendMessage(lastUser.content, { regenerate: true });
  }

  if (!active) return <div className="flex h-screen items-center justify-center bg-[#212121] text-[#ececec]">Loading…</div>;

  const showEmpty = active.messages.length === 0;

  const Sidebar = ({ mobile = false }: { mobile?: boolean }) => (
    <div className={`flex h-full flex-col bg-[#171717] ${mobile ? 'w-[280px]' : ''}`}>
      <div className="flex items-center gap-2 p-2">
        <button onClick={createChat} className="flex flex-1 items-center gap-2 rounded-lg px-3 py-2 text-sm text-[#ececec] hover:bg-white/10 transition"><Icon path={icons.plus} className="h-4 w-4" /> New chat</button>
        <button onClick={() => mobile ? setMobileSidebar(false) : setSidebarOpen(false)} className="rounded-lg p-2 text-[#b4b4b4] hover:bg-white/10 hover:text-white" title="Close sidebar"><Icon path={mobile ? icons.close : icons.side} className="h-4 w-4" /></button>
      </div>
      <div className="flex-1 overflow-y-auto px-2 pb-2">
        <div className="px-2 py-2 text-xs font-medium text-[#8e8e8e]">Recent</div>
        <div className="space-y-0.5">
          {conversations.map(c => (
            <button key={c.id} onClick={() => { setActiveId(c.id); setMobileSidebar(false); }} className={`group flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-left text-sm transition ${c.id === activeId ? 'bg-white/10 text-white' : 'text-[#ececec] hover:bg-white/[0.06]'}`}>
              <span className="min-w-0 flex-1 truncate">{c.title}</span>
              <span onClick={(e) => { e.stopPropagation(); deleteChat(c.id); }} className="rounded p-1 text-[#8e8e8e] opacity-0 hover:bg-white/10 hover:text-white group-hover:opacity-100" title="Delete"><Icon path={icons.trash} className="h-4 w-4" /></span>
            </button>
          ))}
        </div>
      </div>
      <div className="border-t border-white/10 p-3">
        <div className="flex items-center gap-2 rounded-lg px-2 py-2 text-sm text-[#ececec] hover:bg-white/[0.06]">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#10a37f] text-white"><Icon path={icons.spark} className="h-4 w-4" /></div>
          <div className="min-w-0"><div className="truncate font-medium">AETHRIX</div><div className="truncate text-xs text-[#8e8e8e]">{mode.name} · {models.find(m=>m.id===active.model)?.name || active.model}</div></div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-[#212121] text-[#ececec]">
      {mobileSidebar && <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={() => setMobileSidebar(false)}><div className="h-full" onClick={e=>e.stopPropagation()}><Sidebar mobile /></div></div>}
      <aside className={`hidden shrink-0 border-r border-white/10 transition-all duration-200 md:block ${sidebarOpen ? 'w-[260px]' : 'w-0 overflow-hidden border-r-0'}`}><Sidebar /></aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center gap-2 bg-[#212121]/95 px-3 backdrop-blur">
          <button onClick={() => window.innerWidth < 768 ? setMobileSidebar(true) : setSidebarOpen(v => !v)} className="rounded-lg p-2 text-[#b4b4b4] hover:bg-white/10 hover:text-white"><Icon path={icons.menu} className="h-5 w-5" /></button>
          {!sidebarOpen && <button onClick={createChat} className="hidden rounded-lg p-2 text-[#b4b4b4] hover:bg-white/10 hover:text-white md:block" title="New chat"><Icon path={icons.plus} className="h-5 w-5" /></button>}
          <div className="flex min-w-0 items-center gap-2">
            <div className="truncate text-sm font-semibold text-[#ececec]">AETHRIX</div>
            <select value={active.mode} onChange={e=>updateActive(c=>({...c,mode:e.target.value,updatedAt:Date.now()}))} className="rounded-lg bg-transparent px-2 py-1 text-sm text-[#b4b4b4] hover:bg-white/10 focus:outline-none">
              {MODES.map(m => <option key={m.id} value={m.id} className="bg-[#2f2f2f] text-[#ececec]">{m.name}</option>)}
            </select>
            <select value={active.model} onChange={e=>updateActive(c=>({...c,model:e.target.value,updatedAt:Date.now()}))} className="hidden rounded-lg bg-transparent px-2 py-1 text-sm text-[#b4b4b4] hover:bg-white/10 focus:outline-none sm:block">
              {models.map(m => <option key={m.id} value={m.id} className="bg-[#2f2f2f] text-[#ececec]">{m.name || m.id}</option>)}
            </select>
          </div>
          <div className="ml-auto flex items-center gap-1">
            <button onClick={()=>{ if(active){ updateActive(c=>({...c,messages:[],title:'New chat',updatedAt:Date.now()})); } }} className="rounded-lg px-2.5 py-1.5 text-sm text-[#b4b4b4] hover:bg-white/10 hover:text-white">Clear</button>
          </div>
        </header>

        <main className="relative flex-1 overflow-y-auto">
          {showEmpty ? (
            <div className="mx-auto flex min-h-full max-w-3xl flex-col items-center justify-center px-4 pb-32 pt-10 text-center">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-white text-black"><Icon path={icons.spark} className="h-6 w-6" /></div>
              <h1 className="mb-8 text-2xl font-semibold text-white sm:text-3xl">How can I help you today?</h1>
              <div className="grid w-full gap-2 sm:grid-cols-2">
                {PROMPTS.map(p => (
                  <button key={p.title} onClick={() => { setInput(p.text); textareaRef.current?.focus(); }} className="rounded-2xl border border-white/10 bg-transparent p-4 text-left hover:bg-white/[0.04] transition">
                    <div className="text-sm font-medium text-[#ececec]">{p.title}</div>
                    <div className="mt-1 text-sm text-[#8e8e8e] line-clamp-2">{p.text}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="pb-36">
              {active.messages.map((m, idx) => {
                const isUser = m.role === 'user';
                const isLastAssistant = m.role === 'assistant' && idx === active.messages.length - 1;
                return (
                  <div key={m.id} className={`group px-4 py-5 ${isUser ? '' : 'bg-transparent'}`}>
                    <div className={`mx-auto flex max-w-3xl gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
                      <div className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${isUser ? 'bg-[#5b5bd6] text-white' : 'bg-white text-black'}`}>
                        <Icon path={isUser ? icons.user : icons.spark} className="h-4 w-4" />
                      </div>
                      <div className={`min-w-0 flex-1 ${isUser ? 'flex flex-col items-end' : ''}`}>
                        <div className="mb-1 text-sm font-semibold text-white">{isUser ? 'You' : 'AETHRIX'}</div>
                        {editingId === m.id ? (
                          <div className="w-full">
                            <textarea value={editText} onChange={e=>setEditText(e.target.value)} className="w-full rounded-xl border border-white/15 bg-[#2f2f2f] p-3 text-sm outline-none focus:border-white/30" rows={4} />
                            <div className="mt-2 flex justify-end gap-2">
                              <button onClick={()=>setEditingId(null)} className="rounded-lg px-3 py-1.5 text-sm text-[#b4b4b4] hover:bg-white/10">Cancel</button>
                              <button onClick={()=>sendMessage(editText, { fromIndex: idx })} className="rounded-lg bg-white px-3 py-1.5 text-sm font-medium text-black hover:bg-gray-200">Send</button>
                            </div>
                          </div>
                        ) : isUser ? (
                          <div className="max-w-[85%] whitespace-pre-wrap rounded-3xl bg-[#2f2f2f] px-4 py-2.5 text-[15px] leading-7 text-[#ececec]">{m.content}</div>
                        ) : (
                          <div className="min-w-0 text-[15px] leading-7 text-[#ececec]">
                            {m.content ? <Markdown content={m.content} /> : <span className="inline-flex items-center gap-1 text-[#8e8e8e]"><span className="h-2 w-2 animate-pulse rounded-full bg-[#8e8e8e]"></span><span className="h-2 w-2 animate-pulse rounded-full bg-[#8e8e8e] [animation-delay:150ms]"></span><span className="h-2 w-2 animate-pulse rounded-full bg-[#8e8e8e] [animation-delay:300ms]"></span></span>}
                          </div>
                        )}
                        {editingId !== m.id && (
                          <div className={`mt-2 flex items-center gap-1 text-[#8e8e8e] opacity-100 transition md:opacity-0 md:group-hover:opacity-100 ${isUser ? 'justify-end' : ''}`}>
                            <button onClick={()=>copyText(m.content)} className="rounded-md p-1.5 hover:bg-white/10 hover:text-[#ececec]" title="Copy"><Icon path={icons.copy} className="h-4 w-4" /></button>
                            {isUser && <button onClick={()=>{ setEditingId(m.id); setEditText(m.content); }} className="rounded-md p-1.5 hover:bg-white/10 hover:text-[#ececec]" title="Edit"><Icon path={icons.edit} className="h-4 w-4" /></button>}
                            {isLastAssistant && !loading && <button onClick={regenerate} className="rounded-md p-1.5 hover:bg-white/10 hover:text-[#ececec]" title="Regenerate"><Icon path={icons.refresh} className="h-4 w-4" /></button>}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
              {error && <div className="px-4"><div className="mx-auto max-w-3xl rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div></div>}
              <div ref={endRef} />
            </div>
          )}

          <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#212121] via-[#212121] to-transparent pt-10">
            <div className="pointer-events-auto mx-auto max-w-3xl px-4 pb-4">
              <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="rounded-[26px] border border-white/10 bg-[#2f2f2f] shadow-[0_0_0_1px_rgba(255,255,255,0.02)] focus-within:border-white/20">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  placeholder={`Message AETHRIX`}
                  rows={1}
                  className="max-h-[200px] min-h-[52px] w-full resize-none bg-transparent px-5 py-4 text-[15px] text-[#ececec] placeholder:text-[#8e8e8e] outline-none"
                />
                <div className="flex items-center justify-between px-3 pb-3">
                  <div className="flex items-center gap-1 text-xs text-[#8e8e8e]">
                    <span className="rounded-md px-2 py-1">{mode.name}</span>
                  </div>
                  {loading ? (
                    <button type="button" onClick={stop} className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black hover:bg-gray-200" title="Stop"><Icon path={icons.stop} className="h-4 w-4" /></button>
                  ) : (
                    <button type="submit" disabled={!input.trim()} className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black disabled:bg-white/20 disabled:text-[#8e8e8e] hover:bg-gray-200 transition" title="Send"><Icon path={icons.send} className="h-4 w-4" /></button>
                  )}
                </div>
              </form>
              <div className="mt-2 px-2 text-center text-xs text-[#8e8e8e]">AETHRIX can make mistakes. Check important info.</div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
