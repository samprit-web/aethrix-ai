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
    const lang = m[1] || 'text';
    const code = m[2] || '';
    parts.push(
      <div key={key++} className="my-4 overflow-hidden rounded-xl border border-white/10 bg-[#0d0d0d]">
        <div className="flex items-center justify-between bg-white/[0.04] px-4 py-2 text-xs text-[#b4b4b4]">
          <span className="font-medium lowercase">{lang}</span>
          <button
            type="button"
            className="rounded px-2 py-1 hover:bg-white/10 hover:text-white transition"
            onClick={() => navigator.clipboard?.writeText(code)}
          >Copy code</button>
        </div>
        <pre className="overflow-x-auto p-4 text-[13px] leading-6 text-[#ececec]"><code>{code}</code></pre>
      </div>
    );
    last = m.index + m[0].length;
  }
  if (last < content.length) parts.push(<Inline key={key++} text={content.slice(last)} />);
  return <div className="prose-chat text-[15px]">{parts}</div>;
}

function Inline({ text }: { text: string }) {
  const lines = text.split('\n');
  const blocks: React.ReactNode[] = [];
  let list: string[] = [];
  let olist: string[] = [];
  const flush = () => {
    if (list.length) { blocks.push(<ul key={'ul'+blocks.length}>{list.map((x,i)=><li key={i}>{renderInline(x)}</li>)}</ul>); list = []; }
    if (olist.length) { blocks.push(<ol key={'ol'+blocks.length}>{olist.map((x,i)=><li key={i}>{renderInline(x)}</li>)}</ol>); olist = []; }
  };
  for (const raw of lines) {
    if (/^[-*]\s+/.test(raw)) { olist.length && flush(); list.push(raw.replace(/^[-*]\s+/, '')); continue; }
    if (/^\d+\.\s+/.test(raw)) { list.length && flush(); olist.push(raw.replace(/^\d+\.\s+/, '')); continue; }
    flush();
    if (!raw.trim()) { blocks.push(<div key={blocks.length} className="h-2" />); continue; }
    if (/^###\s/.test(raw)) blocks.push(<h4 key={blocks.length}>{renderInline(raw.replace(/^###\s+/, ''))}</h4>);
    else if (/^##\s/.test(raw)) blocks.push(<h3 key={blocks.length}>{renderInline(raw.replace(/^##\s+/, ''))}</h3>);
    else if (/^#\s/.test(raw)) blocks.push(<h2 key={blocks.length}>{renderInline(raw.replace(/^#\s+/, ''))}</h2>);
    else if (/^>\s?/.test(raw)) blocks.push(<blockquote key={blocks.length}>{renderInline(raw.replace(/^>\s?/, ''))}</blockquote>);
    else blocks.push(<p key={blocks.length}>{renderInline(raw)}</p>);
  }
  flush();
  return <>{blocks}</>;
}

function renderInline(text: string): React.ReactNode[] {
  const html = escapeHtml(text);
  const tokens = html.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*\n]+\*|\[[^\]]+\]\([^)]+\))/g);
  return tokens.map((t, i) => {
    if (t.startsWith('`') && t.endsWith('`')) return <code key={i}>{t.slice(1,-1)}</code>;
    if (t.startsWith('**') && t.endsWith('**')) return <strong key={i}>{t.slice(2,-2)}</strong>;
    if (t.startsWith('*') && t.endsWith('*')) return <em key={i}>{t.slice(1,-1)}</em>;
    const lm = t.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (lm) return <a key={i} href={lm[2]} target="_blank" rel="noreferrer">{lm[1]}</a>;
    return <React.Fragment key={i}>{t}</React.Fragment>;
  });
}
