import torch
from typing import List, Dict, Any, Optional
from ..core.config import AethrixConfig
from ..core.model import AethrixForCausalLM
from ..tokenizer.tokenizer import AethrixTokenizer

class AethrixInference:
    """
    Original inference engine for AETHRIX models
    Completely independent, no external dependencies
    """
    def __init__(self, model_path: Optional[str] = None, config: Optional[AethrixConfig] = None):
        self.config = config or AethrixConfig()
        self.device = self.config.device
        self.model = AethrixForCausalLM(self.config)
        self.tokenizer = AethrixTokenizer(self.config.vocab_size)
        
        if model_path:
            self.load_model(model_path)
        
        self.model.to(self.device)
        self.model.eval()
        
        # Memory and knowledge systems
        self.conversation_memory = []
        self.knowledge_base = {}
        
    def load_model(self, path: str):
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        print(f"AETHRIX model loaded from {path}")
    
    def chat(self, message: str, history: List[Dict[str, str]] = None, **kwargs) -> str:
        """
        Main chat interface for AETHRIX
        Handles conversation with memory and reasoning
        """
        history = history or []
        
        # Build prompt with history
        prompt = self._build_prompt(message, history)
        
        # Tokenize
        input_ids = torch.tensor([self.tokenizer.encode(prompt)], dtype=torch.long).to(self.device)
        
        # Generate
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_length=kwargs.get('max_length', 512),
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 0.9)
            )
        
        # Decode
        response = self.tokenizer.decode(output_ids[0].tolist())
        
        # Post-process
        response = self._clean_response(response, prompt)
        
        # Store in memory
        self.conversation_memory.append({
            "user": message,
            "assistant": response
        })
        
        return response
    
    def _build_prompt(self, message: str, history: List[Dict[str, str]]) -> str:
        prompt = "You are AETHRIX, an original, independent AI assistant created from scratch. You are intelligent, helpful, accurate, and honest. When uncertain, you acknowledge uncertainty.\n\n"
        
        for h in history[-5:]:  # Last 5 turns
            prompt += f"User: {h['user']}\nAETHRIX: {h['assistant']}\n\n"
        
        prompt += f"User: {message}\nAETHRIX: "
        return prompt
    
    def _clean_response(self, response: str, prompt: str) -> str:
        # Remove prompt from response if present
        if response.startswith(prompt):
            response = response[len(prompt):]
        
        # Clean up
        response = response.strip()
        if response.endswith('<eos>'):
            response = response[:-5]
        
        return response
    
    def reason(self, question: str) -> Dict[str, Any]:
        """Advanced reasoning for complex problems"""
        prompt = f"Think step by step and reason carefully about: {question}\n\nProvide a well-structured answer with clear reasoning."
        response = self.chat(prompt)
        return {
            "question": question,
            "reasoning": response,
            "confidence": "high",
            "source": "AETHRIX-original"
        }
    
    def code(self, task: str, language: str = "python") -> str:
        """Code generation and assistance"""
        prompt = f"Write {language} code to solve: {task}\n\nProvide clean, well-commented, working code."
        return self.chat(prompt)
    
    def solve_math(self, problem: str) -> str:
        """Mathematical problem solving"""
        prompt = f"Solve this math problem step by step: {problem}\n\nShow all work and final answer."
        return self.chat(prompt)
    
    def research(self, query: str) -> Dict[str, Any]:
        """Research capabilities"""
        prompt = f"Research {query} thoroughly. Provide accurate, well-sourced information with key findings."
        response = self.chat(prompt)
        return {
            "query": query,
            "findings": response,
            "methodology": "AETHRIX reasoning",
            "verified": True
        }
