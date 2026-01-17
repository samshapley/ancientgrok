"""Evaluation metrics for translation quality."""

from typing import List, Dict
from sacrebleu import BLEU, CHRF
import json


class TranslationEvaluator:
    """Computes translation quality metrics."""
    
    def __init__(self):
        """Initialize evaluator with metric calculators."""
        self.bleu = BLEU()
        self.chrf = CHRF()
    
    def evaluate(
        self,
        predictions: List[str],
        references: List[str],
        metadata: List[Dict] = None
    ) -> Dict[str, any]:
        """Evaluate translation predictions against references.
        
        Args:
            predictions: List of predicted translations
            references: List of reference translations
            metadata: Optional list of per-example metadata
            
        Returns:
            Dictionary of evaluation metrics
        """
        assert len(predictions) == len(references), \
            f"Mismatched lengths: {len(predictions)} predictions vs {len(references)} references"
        
        # Compute BLEU
        bleu_score = self.bleu.corpus_score(predictions, [references])
        
        # Compute chrF++
        chrf_score = self.chrf.corpus_score(predictions, [references])
        
        results = {
            "bleu": {
                "score": bleu_score.score,
                "precision": bleu_score.precisions,
                "bp": bleu_score.bp,
                "sys_len": bleu_score.sys_len,
                "ref_len": bleu_score.ref_len
            },
            "chrf": {
                "score": chrf_score.score
            },
            "num_examples": len(predictions)
        }
        
        # Add confidence distribution if metadata provided
        if metadata:
            confidence_dist = {}
            for meta in metadata:
                conf = meta.get("confidence", "unknown")
                confidence_dist[conf] = confidence_dist.get(conf, 0) + 1
            results["confidence_distribution"] = confidence_dist
        
        return results
    
    def evaluate_single(self, prediction: str, reference: str) -> Dict[str, float]:
        """Evaluate a single prediction.
        
        Args:
            prediction: Predicted translation
            reference: Reference translation
            
        Returns:
            Dictionary with sentence-level scores
        """
        bleu_score = self.bleu.sentence_score(prediction, [reference])
        chrf_score = self.chrf.sentence_score(prediction, [reference])
        
        return {
            "bleu": bleu_score.score,
            "chrf": chrf_score.score
        }
    
    def save_results(self, results: Dict, output_path: str):
        """Save evaluation results to JSON file.
        
        Args:
            results: Results dictionary
            output_path: Output file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def print_results(results: Dict):
        """Pretty print results.
        
        Args:
            results: Results dictionary from evaluate()
        """
        print(f"\n{'='*60}")
        print("TRANSLATION EVALUATION RESULTS")
        print(f"{'='*60}")
        print(f"Number of examples: {results['num_examples']}")
        print(f"\nBLEU Score: {results['bleu']['score']:.2f}")
        print(f"  - BP (Brevity Penalty): {results['bleu']['bp']:.4f}")
        print(f"  - System length: {results['bleu']['sys_len']}")
        print(f"  - Reference length: {results['bleu']['ref_len']}")
        print(f"\nchrF++ Score: {results['chrf']['score']:.2f}")
        
        if "confidence_distribution" in results:
            print(f"\nConfidence Distribution:")
            for conf, count in results["confidence_distribution"].items():
                pct = (count / results['num_examples']) * 100
                print(f"  - {conf}: {count} ({pct:.1f}%)")
        print(f"{'='*60}\n")