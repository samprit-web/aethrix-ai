export type Role = 'user' | 'assistant' | 'system';
export type Message = {
  id: string;
  role: Role;
  content: string;
  createdAt: number;
  status?: 'streaming' | 'done' | 'error';
};

export type Conversation = {
  id: string;
  title: string;
  messages: Message[];
  updatedAt: number;
  mode: string;
  model: string;
};

export const MODES = [
  { id: 'assistant', name: 'Assistant', prompt: 'You are AETHRIX, a highly intelligent, helpful AI assistant. Be accurate, clear, and proactive. Use structured formatting when useful.' },
  { id: 'coder', name: 'Coding', prompt: 'You are AETHRIX Coder, an expert software engineer. Provide correct, secure, production-minded code with explanations when needed.' },
  { id: 'writer', name: 'Writing', prompt: 'You are AETHRIX Writer. Produce clear, engaging, well-structured writing tailored to the user’s goal and audience.' },
  { id: 'research', name: 'Research', prompt: 'You are AETHRIX Research. Analyze questions carefully, separate facts from assumptions, and present findings clearly.' },
  { id: 'tutor', name: 'Learning', prompt: 'You are AETHRIX Tutor. Teach step by step, adapt to the user’s level, and check concise examples.' },
  { id: 'planner', name: 'Planning', prompt: 'You are AETHRIX Planner. Turn goals into concrete plans with priorities, dependencies, risks, and next actions.' },
];

export const MODELS = [
  { id: 'auto', name: 'Auto' },
  { id: 'llama3.1', name: 'Fast' },
  { id: 'qwen2.5:7b', name: 'Balanced' },
  { id: 'deepseek-r1:8b', name: 'Reasoning' },
];

export const PROMPTS = [
  { title: 'Summarize content', text: 'Summarize the following and extract key action items:\n' },
  { title: 'Write code', text: 'Help me write code for: ' },
  { title: 'Explain a concept', text: 'Explain this concept clearly with a simple example: ' },
  { title: 'Draft an email', text: 'Draft a professional email about: ' },
  { title: 'Plan a project', text: 'Create a step-by-step plan for: ' },
  { title: 'Analyze tradeoffs', text: 'Compare these options with pros, cons, and a recommendation: ' },
];

const KEY = 'aethrix.conversations.v2';

export function uid() { return Math.random().toString(36).slice(2) + Date.now().toString(36); }

export function loadConversations(): Conversation[] {
  if (typeof window === 'undefined') return [];
  try {
    const v2 = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (Array.isArray(v2) && v2.length) return v2;
    const v1 = JSON.parse(localStorage.getItem('aethrix.conversations.v1') || '[]');
    return Array.isArray(v1) ? v1 : [];
  } catch { return []; }
}

export function saveConversations(items: Conversation[]) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(KEY, JSON.stringify(items.slice(0, 60)));
}

export function newConversation(mode = 'assistant', model = 'auto'): Conversation {
  return { id: uid(), title: 'New chat', mode, model, updatedAt: Date.now(), messages: [] };
}

export function titleFrom(text: string) {
  const t = text.replace(/\s+/g, ' ').trim();
  return t.length > 44 ? t.slice(0, 44) + '…' : t || 'New chat';
}
