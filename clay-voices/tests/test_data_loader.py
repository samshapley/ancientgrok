"""Tests for data loading functionality."""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_loader import ParallelCorpus


def test_corpus_loads():
    """Test that the corpus loads without errors."""
    corpus = ParallelCorpus("data")
    assert corpus.train_pairs is not None
    assert corpus.test_pairs is not None


def test_corpus_stats():
    """Test that corpus statistics are computed correctly."""
    corpus = ParallelCorpus("data")
    stats = corpus.stats()
    
    assert "train_size" in stats
    assert "test_size" in stats
    assert "total" in stats
    assert stats["total"] == stats["train_size"] + stats["val_size"] + stats["test_size"]


def test_few_shot_sampling():
    """Test few-shot example sampling."""
    corpus = ParallelCorpus("data")
    
    # Sample 5 examples
    few_shot = corpus.sample_few_shot(5, seed=42)
    assert len(few_shot) == 5
    
    # Should be tuples
    for example in few_shot:
        assert isinstance(example, tuple)
        assert len(example) == 2
        assert isinstance(example[0], str)  # Sumerian
        assert isinstance(example[1], str)  # English


def test_sampling_reproducibility():
    """Test that sampling with same seed gives same results."""
    corpus = ParallelCorpus("data")
    
    sample1 = corpus.sample_few_shot(10, seed=42)
    sample2 = corpus.sample_few_shot(10, seed=42)
    
    assert sample1 == sample2


def test_test_subset():
    """Test test set subsetting."""
    corpus = ParallelCorpus("data")
    
    # Get subset
    subset = corpus.get_test_subset(50, seed=99)
    assert len(subset) == 50
    
    # Get all (None)
    all_test = corpus.get_test_subset(None)
    assert len(all_test) == len(corpus.test_pairs)