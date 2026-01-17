"""Data loading utilities for Sumerian-English and Egyptian-English parallel corpora."""

from pathlib import Path
from typing import List, Tuple
import random


class ParallelCorpus:
    """Loads and manages parallel ancient language-English text data.
    
    Supports both Sumerian-English and Egyptian-English translation datasets.
    """
    
    def __init__(self, data_dir: str = "data", dataset: str = "sumerian"):
        """Initialize corpus loader.
        
        Args:
            data_dir: Directory containing parallel text files
            dataset: Which dataset to load ('sumerian' or 'egyptian')
        """
        self.data_dir = Path(data_dir)
        self.dataset = dataset
        
        # Configure file prefixes based on dataset
        if dataset == "egyptian":
            self.source_prefix = "egyptian"
            self.target_prefix = "english_egy"
        else:
            self.source_prefix = "sumerian"
            self.target_prefix = "english"
        
        self.train_pairs = self._load_split("train")
        self.val_pairs = self._load_split("val")
        self.test_pairs = self._load_split("test")
        
        # Load monolingual Sumerian corpus for context priming
        self.monolingual_sumerian = self._load_monolingual() if dataset == "sumerian" else []
        
    def _load_split(self, split: str) -> List[Tuple[str, str]]:
        """Load a data split.
        
        Args:
            split: One of 'train', 'val', 'test'
            
        Returns:
            List of (source_language, english) tuples
        """
        source_file = self.data_dir / f"{self.source_prefix}_{split}.txt"
        target_file = self.data_dir / f"{self.target_prefix}_{split}.txt"
        
        if not source_file.exists() or not target_file.exists():
            return []
            
        with open(source_file, 'r', encoding='utf-8') as f_src:
            source_lines = [line.strip() for line in f_src if line.strip()]
            
        with open(target_file, 'r', encoding='utf-8') as f_eng:
            english_lines = [line.strip() for line in f_eng if line.strip()]
            
        assert len(source_lines) == len(english_lines), \
            f"Mismatched lengths: {len(source_lines)} vs {len(english_lines)}"
            
        return list(zip(source_lines, english_lines))
    
    def _load_monolingual(self) -> List[str]:
        """Load monolingual Sumerian corpus.
        
        Returns:
            List of Sumerian sentences (no translations)
        """
        mono_file = self.data_dir / "Sumerian_monolingual_processed.txt"
        
        if not mono_file.exists():
            return []
        
        with open(mono_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        return lines
    
    def sample_few_shot(self, n: int, seed: int = 42) -> List[Tuple[str, str]]:
        """Sample n examples for few-shot prompting from training set.
        
        Args:
            n: Number of examples to sample
            seed: Random seed for reproducibility
            
        Returns:
            List of (sumerian, english) example pairs
        """
        random.seed(seed)
        return random.sample(self.train_pairs, min(n, len(self.train_pairs)))
    
    def sample_monolingual(self, n: int, seed: int = 42) -> List[str]:
        """Sample n examples from monolingual Sumerian corpus for context priming.
        
        Args:
            n: Number of monolingual sentences to sample
            seed: Random seed for reproducibility
            
        Returns:
            List of Sumerian sentences (no translations)
        """
        if not self.monolingual_sumerian:
            return []
        
        random.seed(seed)
        return random.sample(self.monolingual_sumerian, min(n, len(self.monolingual_sumerian)))
    
    def get_test_subset(self, n: int = None, seed: int = 42) -> List[Tuple[str, str]]:
        """Get test subset for evaluation.
        
        Args:
            n: Number of test examples (None = all)
            seed: Random seed if sampling
            
        Returns:
            Test pairs
        """
        if n is None or n >= len(self.test_pairs):
            return self.test_pairs
            
        random.seed(seed)
        return random.sample(self.test_pairs, n)
    
    def stats(self) -> dict:
        """Return dataset statistics."""
        return {
            "dataset": self.dataset,
            "train_size": len(self.train_pairs),
            "val_size": len(self.val_pairs),
            "test_size": len(self.test_pairs),
            "total": len(self.train_pairs) + len(self.val_pairs) + len(self.test_pairs),
            "monolingual_sumerian_size": len(self.monolingual_sumerian)
        }


if __name__ == "__main__":
    # Test data loading
    corpus = ParallelCorpus()
    print("Dataset Statistics:")
    print(corpus.stats())
    
    print("\nFirst training example:")
    print(f"Sumerian: {corpus.train_pairs[0][0]}")
    print(f"English: {corpus.train_pairs[0][1]}")
    
    print("\nSample 3-shot examples:")
    few_shot = corpus.sample_few_shot(3)
    for i, (sum_text, eng_text) in enumerate(few_shot, 1):
        print(f"{i}. {sum_text} → {eng_text}")