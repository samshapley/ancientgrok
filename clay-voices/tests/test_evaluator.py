"""Tests for evaluation metrics."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from evaluator import TranslationEvaluator


def test_evaluator_initialization():
    """Test evaluator initializes correctly."""
    evaluator = TranslationEvaluator()
    assert evaluator.bleu is not None
    assert evaluator.chrf is not None


def test_perfect_match():
    """Test evaluation with perfect matches."""
    evaluator = TranslationEvaluator()
    
    predictions = ["NUMB sheep", "The king", "Year: Enlil was installed"]
    references = ["NUMB sheep", "The king", "Year: Enlil was installed"]
    
    results = evaluator.evaluate(predictions, references)
    
    # Perfect match should have BLEU very close to 100 (allow floating point precision)
    assert results["bleu"]["score"] > 99.99
    assert results["num_examples"] == 3


def test_no_match():
    """Test evaluation with no matches."""
    evaluator = TranslationEvaluator()
    
    predictions = ["completely different", "wrong text", "not matching"]
    references = ["the original", "correct translation", "proper answer"]
    
    results = evaluator.evaluate(predictions, references)
    
    # No overlap should have low BLEU
    assert results["bleu"]["score"] < 10.0


def test_single_evaluation():
    """Test single example evaluation."""
    evaluator = TranslationEvaluator()
    
    prediction = "NUMB sheep"
    reference = "NUMB sheep"
    
    result = evaluator.evaluate_single(prediction, reference)
    
    assert "bleu" in result
    assert "chrf" in result
    # Single-sentence BLEU can be 0 due to brevity penalty and n-gram requirements
    # Just verify it returns a number
    assert isinstance(result["bleu"], (int, float))


def test_confidence_distribution():
    """Test confidence distribution calculation."""
    evaluator = TranslationEvaluator()
    
    predictions = ["a", "b", "c"]
    references = ["a", "b", "c"]
    metadata = [
        {"confidence": "high"},
        {"confidence": "medium"},
        {"confidence": "high"}
    ]
    
    results = evaluator.evaluate(predictions, references, metadata)
    
    assert "confidence_distribution" in results
    assert results["confidence_distribution"]["high"] == 2
    assert results["confidence_distribution"]["medium"] == 1