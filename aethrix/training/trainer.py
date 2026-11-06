import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from typing import Optional
import os
from ..core.config import AethrixConfig
from ..core.model import AethrixForCausalLM

class AethrixDataset(Dataset):
    """Dataset for AETHRIX training"""
    def __init__(self, texts, tokenizer, max_length=4096):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = []
        for text in texts:
            tokens = tokenizer.encode(text)
            if len(tokens) > max_length:
                tokens = tokens[:max_length]
            self.examples.append(tokens)
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        tokens = self.examples[idx]
        input_ids = torch.tensor(tokens, dtype=torch.long)
        labels = input_ids.clone()
        return {"input_ids": input_ids, "labels": labels}

class AethrixTrainer:
    """Original training system for AETHRIX"""
    def __init__(self, model: AethrixForCausalLM, config: AethrixConfig):
        self.model = model
        self.config = config
        self.device = config.device
        self.model.to(self.device)
        
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
    
    def train(self, train_dataset, epochs=1):
        """Train the model"""
        self.model.train()
        dataloader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
        
        for epoch in range(epochs):
            total_loss = 0
            for step, batch in enumerate(dataloader):
                input_ids = batch["input_ids"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                outputs = self.model(input_ids, labels=labels)
                loss = outputs["loss"]
                loss = loss / self.config.gradient_accumulation_steps
                loss.backward()
                
                if (step + 1) % self.config.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                
                total_loss += loss.item()
                if step % 100 == 0:
                    print(f"Epoch {epoch}, Step {step}, Loss: {loss.item():.4f}")
            
            print(f"Epoch {epoch} completed, Avg Loss: {total_loss/len(dataloader):.4f}")
    
    def save_checkpoint(self, path: str):
        """Save model checkpoint"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
        }, path)
        print(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Checkpoint loaded from {path}")
