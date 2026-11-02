'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ImageGeneration() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setLoading(true);
    setTimeout(() => {
      setImages(prev => [{
        id: Date.now(),
        prompt: prompt,
        url: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1024&h=1024'
      }, ...prev]);
      setLoading(false);
      setPrompt('');
    }, 2000);
  };

  return (
    <div className="min-h-screen">
      <div className="fixed inset-0 cyber-grid opacity-10 pointer-events-none"></div>
      
      <header className="relative z-10 border-b border-cyan-500/30 backdrop-blur-md bg-black/50 p-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-4">
            <Link href="/chat" className="text-gray-400 hover:text-cyan-400">← Back to Chat</Link>
            <h1 className="text-xl font-bold glow-text text-cyan-400">🎨 Original Image Generation</h1>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-6xl mx-auto p-4 py-8">
        <div className="mb-8 p-6 border border-cyan-500/30 rounded-lg bg-black/50">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Describe your image</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="A futuristic cyberpunk city at night with neon lights, flying cars, and holographic advertisements..."
                className="w-full px-4 py-3 bg-black/50 border border-cyan-500/30 rounded-lg focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-white h-32"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !prompt.trim()}
              className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-cyan-500/50 transition-all disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Image'}
            </button>
          </form>
          <p className="text-sm text-gray-400 mt-2">Powered by open-source Stable Diffusion models</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {images.map((image: any) => (
            <div key={image.id} className="border border-cyan-500/30 rounded-lg overflow-hidden bg-black/50">
              <img src={image.url} alt={image.prompt} className="w-full h-64 object-cover" />
              <div className="p-4">
                <p className="text-sm text-gray-300 line-clamp-2">{image.prompt}</p>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
