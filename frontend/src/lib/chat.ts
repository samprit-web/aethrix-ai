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
  { id: 'coder', name: 'Coder', prompt: 'You are AETHRIX Coder, an expert software engineer. Provide correct, secure, production-minded code with explanations when needed.' },
  { id: 'writer', name: 'Writer', prompt: 'You are AETHRIX Writer. Produce clear, engaging, well-structured writing tailored to the user’s goal and audience.' },
  { id: 'research', name: 'Research', prompt: 'You are AETHRIX Research. Analyze questions carefully, separate facts from assumptions, and present findings clearly.' },
  { id: 'tutor', name: 'Tutor', prompt: 'You are AETHRIX Tutor. Teach step by step, adapt to the user’s level, and check concise examples.' },
];

export const MODELS = [
  { id: 'auto', name: 'AETHRIX Auto' },
  { id: 'llama-3.1-8b', name: 'Llama 3.1 8B' },
  { id: 'qwen2.5-7b', name: 'Qwen 2.5 7B' },
  { id: 'mistral', name: 'Mistral' },
];

export const PROMPTS = [
  'Summarize this and extract action items.',
  'Explain this concept simply, then give an advanced view.',
  'Review this code for bugs, security, and improvements.',
  'Draft a professional email for this situation.',
  'Create a step-by-step plan to accomplish this goal.',
  'Compare options with pros, cons, and a recommendation.',
];

const KEY = 'aethrix.conversations.v1';

export function uid() { return Math.random().toString(36).slice(2) + Date.now().toString(36); }

export function loadConversations(): Conversation[] {
  if (typeof window === 'undefined') return [];
  try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; }
}

export function saveConversations(items: Conversation[]) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(KEY, JSON.stringify(items.slice(0, 50)));
}

export function newConversation(mode = 'assistant', model = 'auto'): Conversation {
  return {
    id: uid(),
    title: 'New chat',
    mode,
    model,
    updatedAt: Date.now(),
    messages: [{ id: uid(), role: 'assistant', content: 'Hi — I’m **AETHRIX**, a highly capable AI assistant. I can help with reasoning, coding, writing, research, planning, analysis, and more. What are we working on?', createdAt: Date.now(), status: 'done' }],
  };
}

export function titleFrom(text: string) {
  const t = text.replace(/\s+/g, ' ').trim();
  return t.length > 48 ? t.slice(0, 48) + '…' : t || 'New chat';
}
