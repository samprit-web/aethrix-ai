'use client';

import React from 'react';

function escapeHtml(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export function Markdown({ content }: { content: string }) {
  const parts: React.ReactNode[] = [];
  const codeBlock = /```(\w+)?\n([\s\S]*?)```/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let key = 0;
  while ((m = codeBlock.exec(content)) !== null) {
    if (m.index > last) parts.push(<Inline key={key++} text={content.slice(last, m.index)} />);
    const lang = m[1] || '';
    const code = m[2] || '';
    parts.push(
      <div key={key++} className="my-3 overflow-hidden rounded-lg border border-cyan-500/20 bg-[#050814]">
        <div className="flex items-center justify-between border-b border-cyan-500/10 px-3 py-1.5 text-xs text-gray-400">
          <span>{lang || 'code'}</span>
          <button className="hover:text-cyan-300" onClick={() => navigator.clipboard?.writeText(code)}>Copy</button>
        </div>
        <pre className="overflow-x-auto p-3 text-sm leading-6 text-gray-100"><code>{code}</code></pre>
      </div>
    );
    last = m.index + m[0].length;
  }
  if (last < content.length) parts.push(<Inline key={key++} text={content.slice(last)} />);
  return <div className="markdown space-y-2 break-words">{parts}</div>;
}

function Inline({ text }: { text: string }) {
  const lines = text.split('\n');
  const blocks: React.ReactNode[] = [];
  let list: string[] = [];
  let olist: string[] = [];
  const flush = () => {
    if (list.length) { blocks.push(<ul key={'ul'+blocks.length} className="ml-5 list-disc space-y-1">{list.map((x,i)=><li key={i}>{renderInline(x)}</li>)}</ul>); list = []; }
    if (olist.length) { blocks.push(<ol key={'ol'+blocks.length} className="ml-5 list-decimal space-y-1">{olist.map((x,i)=><li key={i}>{renderInline(x)}</li>)}</ol>); olist = []; }
  };
  for (const raw of lines) {
    const line = raw;
    if (/^[-*]\s+/.test(line)) { olist.length && flush(); list.push(line.replace(/^[-*]\s+/, '')); continue; }
    if (/^\d+\.\s+/.test(line)) { list.length && flush(); olist.push(line.replace(/^\d+\.\s+/, '')); continue; }
    flush();
    if (!line.trim()) { blocks.push(<div key={blocks.length} className="h-1" />); continue; }
    if (/^###\s/.test(line)) blocks.push(<h4 key={blocks.length} className="pt-1 text-base font-semibold text-cyan-200">{renderInline(line.replace(/^###\s+/, ''))}</h4>);
    else if (/^##\s/.test(line)) blocks.push(<h3 key={blocks.length} className="pt-1 text-lg font-semibold text-cyan-100">{renderInline(line.replace(/^##\s+/, ''))}</h3>);
    else if (/^#\s/.test(line)) blocks.push(<h2 key={blocks.length} className="pt-1 text-xl font-semibold text-white">{renderInline(line.replace(/^#\s+/, ''))}</h2>);
    else if (/^>\s?/.test(line)) blocks.push(<blockquote key={blocks.length} className="border-l-2 border-cyan-500/40 pl-3 text-gray-300">{renderInline(line.replace(/^>\s?/, ''))}</blockquote>);
    else blocks.push(<p key={blocks.length} className="leading-7 text-gray-100">{renderInline(line)}</p>);
  }
  flush();
  return <>{blocks}</>;
}

function renderInline(text: string): React.ReactNode[] {
  const html = escapeHtml(text);
  const tokens = html.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*\n]+\*|\[[^\]]+\]\([^)]+\))/g);
  return tokens.map((t, i) => {
    if (t.startsWith('`') && t.endsWith('`')) return <code key={i} className="rounded bg-cyan-500/10 px-1.5 py-0.5 text-[0.92em] text-cyan-100">{t.slice(1,-1)}</code>;
    if (t.startsWith('**') && t.endsWith('**')) return <strong key={i} className="font-semibold text-white">{t.slice(2,-2)}</strong>;
    if (t.startsWith('*') && t.endsWith('*')) return <em key={i} className="text-gray-200">{t.slice(1,-1)}</em>;
    const lm = t.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (lm) return <a key={i} href={lm[2]} target="_blank" rel="noreferrer" className="text-cyan-300 underline decoration-cyan-500/40 underline-offset-2">{lm[1]}</a>;
    return <React.Fragment key={i}>{t}</React.Fragment>;
  });
}
