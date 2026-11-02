'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Welcome to AETHRIX AI! I\'m your independent AI assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    setTimeout(() => {
      const assistantMessage = { 
        role: 'assistant', 
        content: 'I\'m AETHRIX AI, running on independent open-source infrastructure. I can help with chat, analysis, writing, coding, and much more. What would you like to explore?' 
      };
      setMessages(prev => [...prev, assistantMessage]);
      setLoading(false);
    }, 1000);
  };

  const tools = [
    { name: "Image Gen", href: "/tools/image", icon: "🎨" },
    { name: "Email Draft", href: "/tools/email", icon: "✉️" },
    { name: "Document", href: "/tools/document", icon: "📄" },
    { name: "Research", href: "/tools/research", icon: "🔍" },
    { name: "Meeting", href: "/tools/meeting", icon: "📅" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <div className="fixed inset-0 cyber-grid opacity-10 pointer-events-none"></div>
      
      {/* Header */}
      <header className="relative z-10 border-b border-cyan-500/30 backdrop-blur-md bg-black/50 p-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <Link href="/" className="text-xl font-bold glow-text text-cyan-400">AETHRIX AI</Link>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-green-400">● Independent • Free</span>
            <Link href="/dashboard" className="text-gray-300 hover:text-cyan-400">Dashboard</Link>
          </div>
        </div>
      </header>

      {/* Tools Bar */}
      <div className="relative z-10 border-b border-cyan-500/20 bg-black/30 p-2">
        <div className="flex items-center space-x-4 max-w-7xl mx-auto overflow-x-auto">
          {tools.map((tool, index) => (
            <Link
              key={index}
              href={tool.href}
              className="flex items-center space-x-2 px-3 py-1 rounded-lg hover:bg-cyan-500/10 transition-colors whitespace-nowrap"
            >
              <span>{tool.icon}</span>
              <span className="text-sm text-gray-300">{tool.name}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <main className="relative z-10 flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] p-4 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-cyan-500 to-purple-500'
                    : 'border border-cyan-500/30 bg-black/50'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="border border-cyan-500/30 bg-black/50 p-4 rounded-lg">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Input Area */}
      <div className="relative z-10 border-t border-cyan-500/30 bg-black/50 p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message AETHRIX AI..."
            className="flex-1 px-4 py-3 bg-black/50 border border-cyan-500/30 rounded-lg focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-white"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-cyan-500/50 transition-all disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
