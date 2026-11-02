'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function Home() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const features = [
    { name: "AI Chat", icon: "💬", desc: "Intelligent conversations with open-source models" },
    { name: "Image Generation", icon: "🎨", desc: "Create original images from text descriptions" },
    { name: "Email Drafting", icon: "✉️", desc: "AI-powered email composition and refinement" },
    { name: "Meeting Scheduling", icon: "📅", desc: "Smart scheduling assistant for your calendar" },
    { name: "Document Creation", icon: "📄", desc: "Generate reports, presentations and documents" },
    { name: "Research Tools", icon: "🔍", desc: "Deep research and analysis capabilities" },
    { name: "Productivity Suite", icon: "⚡", desc: "Summaries, translations and code assistance" },
  ];

  return (
    <div className="min-h-screen relative">
      {/* Animated background grid */}
      <div className="fixed inset-0 cyber-grid opacity-20 pointer-events-none"></div>
      
      {/* Navigation */}
      <nav className="relative z-10 border-b border-cyan-500/30 backdrop-blur-md bg-black/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold glow-text text-cyan-400">AETHRIX AI</h1>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-300 hover:text-cyan-400 transition-colors">Features</a>
              <a href="#about" className="text-gray-300 hover:text-cyan-400 transition-colors">About</a>
              <a href="#pricing" className="text-gray-300 hover:text-cyan-400 transition-colors">Pricing</a>
              <Link href="/auth/login" className="text-gray-300 hover:text-cyan-400 transition-colors">Login</Link>
              <Link href="/auth/register" className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition-all">
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="glow-text text-cyan-400">AETHRIX</span>
              <br />
              <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                INTELLIGENCE
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              The world's first completely independent AI platform. Free forever, no ads, no corporate dependencies.
            </p>
            <p className="text-lg text-gray-400 mb-12 max-w-2xl mx-auto">
              AI Chat • Original Image Generation • Email Drafting • Meeting Scheduling • Document Creation • Research & Productivity Tools
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/chat" className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg text-lg font-semibold hover:shadow-lg hover:shadow-cyan-500/50 transition-all float-animation">
                Start Using AETHRIX Free
              </Link>
              <Link href="#features" className="px-8 py-4 border border-cyan-500/50 rounded-lg text-lg font-semibold hover:bg-cyan-500/10 transition-all">
                Explore Features
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 glow-text text-cyan-400">
              POWERFUL FEATURES
            </h2>
            <p className="text-xl text-gray-400">Everything you need, built independently from the ground up</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="p-6 border border-cyan-500/30 rounded-lg bg-black/30 backdrop-blur-sm hover:border-cyan-400 hover:shadow-lg hover:shadow-cyan-500/20 transition-all"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2 text-cyan-400">{feature.name}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="relative z-10 py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-8 glow-text text-cyan-400">
            INDEPENDENT BY DESIGN
          </h2>
          <div className="space-y-6 text-lg text-gray-300">
            <p>
              AETHRIX AI is built from scratch with original architecture. No dependency on ChatGPT, Gemini, Grok or any other commercial AI APIs.
            </p>
            <p>
              Powered by open-source models that can run independently on our own infrastructure or yours. Free public access worldwide with no advertisements ever.
            </p>
            <p>
              Sustainable through optional premium services, donations and subscriptions only. Your privacy and freedom are our priorities.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="p-8 border border-cyan-500/50 rounded-lg bg-gradient-to-r from-cyan-500/10 to-purple-500/10 backdrop-blur-sm">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 glow-text text-cyan-400">
              JOIN THE INDEPENDENT AI REVOLUTION
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Free access for everyone, worldwide. No ads, no corporate control.
            </p>
            <Link href="/auth/register" className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg text-lg font-semibold hover:shadow-lg hover:shadow-cyan-500/50 transition-all inline-block">
              Create Your Free Account
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-cyan-500/30 py-8 px-4">
        <div className="max-w-7xl mx-auto text-center text-gray-400">
          <p className="mb-2">© 2024 AETHRIX AI. Independently owned and operated.</p>
          <p className="text-sm">Free to use worldwide • No advertisements • Open architecture</p>
        </div>
      </footer>
    </div>
  );
}
