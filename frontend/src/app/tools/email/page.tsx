'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function EmailDraft() {
  const [formData, setFormData] = useState({
    purpose: '',
    recipient: '',
    tone: 'professional',
    details: ''
  });
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setDraft(`Subject: ${formData.purpose}

Dear ${formData.recipient},

I hope this message finds you well. 

Regarding ${formData.purpose.toLowerCase()}, I wanted to reach out as discussed.

${formData.details ? formData.details + '\n\n' : ''}
Please let me know if you need any additional information or if there's anything else I can do to help.

Best regards,
[Your Name]`);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen">
      <div className="fixed inset-0 cyber-grid opacity-10 pointer-events-none"></div>
      
      <header className="relative z-10 border-b border-cyan-500/30 backdrop-blur-md bg-black/50 p-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-4">
            <Link href="/chat" className="text-gray-400 hover:text-cyan-400">← Back to Chat</Link>
            <h1 className="text-xl font-bold glow-text text-cyan-400">✉️ Email Drafting Assistant</h1>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-6xl mx-auto p-4 py-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="p-6 border border-cyan-500/30 rounded-lg bg-black/50">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Purpose</label>
              <input
                type="text"
                value={formData.purpose}
                onChange={(e) => setFormData({...formData, purpose: e.target.value})}
                placeholder="Follow up on meeting, Job application, etc."
                className="w-full px-4 py-2 bg-black/50 border border-cyan-500/30 rounded-lg focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Recipient</label>
              <input
                type="text"
                value={formData.recipient}
                onChange={(e) => setFormData({...formData, recipient: e.target.value})}
                placeholder="John Doe or john@example.com"
                className="w-full px-4 py-2 bg-black/50 border border-cyan-500/30 rounded-lg focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Tone</label>
              <select
                value={formData.tone}
                onChange={(e) => setFormData({...formData, tone: e.target.value})}
                className="w-full px-4 py-2 bg-black/50 border border-cyan-500/30 rounded-lg focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-white"
              >
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="formal">Formal</option>
                <option value="casual">Casual</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Additional Details</label>
              <textarea
                value={formData.details}
                onChange={(e) => setFormData({...formData, details: e.target.value})}
                placeholder="Any specific details to include..."
                className="w-full px-4 py-2 bg-black/50 border border-cyan-500/30 rounded-lg focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-white h-24"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-cyan-500/50 transition-all disabled:opacity-50"
            >
              {loading ? 'Drafting...' : 'Generate Email Draft'}
            </button>
          </form>
        </div>

        <div className="p-6 border border-cyan-500/30 rounded-lg bg-black/50">
          <h2 className="text-lg font-semibold text-cyan-400 mb-4">Generated Draft</h2>
          {draft ? (
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              className="w-full h-96 px-4 py-3 bg-black/50 border border-cyan-500/30 rounded-lg focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-white"
            />
          ) : (
            <div className="h-96 flex items-center justify-center text-gray-500">
              Your email draft will appear here
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
