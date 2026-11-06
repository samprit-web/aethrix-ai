import json
import re
from collections import defaultdict
from typing import List, Dict, Tuple

class AethrixTokenizer:
    """
    Original Byte Pair Encoding (BPE) tokenizer built from scratch
    No dependency on external tokenizers
    """
    def __init__(self, vocab_size=50000):
        self.vocab_size = vocab_size
        self.word2idx = {}
        self.idx2word = {}
        self.bpe_ranks = {}
        self.special_tokens = {
            '<pad>': 0,
            '<unk>': 1,
            '<bos>': 2,
            '<eos>': 3,
            '<mask>': 4,
        }
        self._initialize()
    
    def _initialize(self):
        # Initialize with basic vocabulary
        for token, idx in self.special_tokens.items():
            self.word2idx[token] = idx
            self.idx2word[idx] = token
        
        # Add basic characters and common patterns
        idx = len(self.special_tokens)
        for i in range(ord(' '), ord('~') + 1):
            char = chr(i)
            if char not in self.word2idx:
                self.word2idx[char] = idx
                self.idx2word[idx] = char
                idx += 1
        
        # Fill remaining with placeholder tokens
        while idx < self.vocab_size:
            token = f'<token_{idx}>'
            self.word2idx[token] = idx
            self.idx2word[idx] = token
            idx += 1
    
    def train(self, texts: List[str], vocab_size: int = None):
        """Train BPE tokenizer on corpus"""
        if vocab_size:
            self.vocab_size = vocab_size
        
        # Get word frequencies
        word_freqs = defaultdict(int)
        for text in texts:
            words = self._split_words(text)
            for word in words:
                word_freqs[' '.join(list(word)) + ' </w>'] += 1
        
        # BPE merges
        num_merges = self.vocab_size - len(self.word2idx)
        for i in range(num_merges):
            pairs = self._get_pair_freqs(word_freqs)
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            self.bpe_ranks[best] = i
            word_freqs = self._merge_vocab(best, word_freqs)
        
        print(f"Trained AETHRIX tokenizer with {len(self.word2idx)} tokens")
    
    def _split_words(self, text):
        # Simple word splitting
        return re.findall(r'\S+|\n|\t', text)
    
    def _get_pair_freqs(self, word_freqs):
        pairs = defaultdict(int)
        for word, freq in word_freqs.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs
    
    def _merge_vocab(self, pair, word_freqs):
        new_word_freqs = {}
        bigram = re.escape(' '.join(pair))
        p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
        for word in word_freqs:
            w_out = p.sub(''.join(pair), word)
            new_word_freqs[w_out] = word_freqs[word]
        return new_word_freqs
    
    def encode(self, text: str, add_special_tokens=True) -> List[int]:
        """Encode text to token ids"""
        tokens = []
        if add_special_tokens:
            tokens.append(self.word2idx['<bos>'])
        
        # Simple encoding
        words = self._split_words(text)
        for word in words:
            if word in self.word2idx:
                tokens.append(self.word2idx[word])
            else:
                # Character-level fallback
                for char in word:
                    if char in self.word2idx:
                        tokens.append(self.word2idx[char])
                    else:
                        tokens.append(self.word2idx['<unk>'])
        
        if add_special_tokens:
            tokens.append(self.word2idx['<eos>'])
        return tokens
    
    def decode(self, token_ids: List[int]) -> str:
        """Decode token ids to text"""
        tokens = []
        for tid in token_ids:
            if tid in self.idx2word:
                token = self.idx2word[tid]
                if token in ['<bos>', '<eos>', '<pad>']:
                    continue
                tokens.append(token)
            else:
                tokens.append('<unk>')
        return ''.join(tokens).replace('</w>', ' ')
    
    def save(self, path: str):
        """Save tokenizer"""
        data = {
            'word2idx': self.word2idx,
            'bpe_ranks': {str(k): v for k, v in self.bpe_ranks.items()},
            'vocab_size': self.vocab_size
        }
        with open(path, 'w') as f:
            json.dump(data, f)
    
    def load(self, path: str):
        """Load tokenizer"""
        with open(path, 'r') as f:
            data = json.load(f)
        self.word2idx = data['word2idx']
        self.idx2word = {int(v): k for k, v in self.word2idx.items()}
        self.bpe_ranks = {tuple(k.strip('()').split(', ')): v for k, v in data['bpe_ranks'].items()}
        self.vocab_size = data['vocab_size']
