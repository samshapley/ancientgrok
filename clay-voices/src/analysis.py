"""Analysis utilities for translation results."""

import json
from pathlib import Path
from typing import Dict, List
import pandas as pd


class ResultsAnalyzer:
    """Analyze and visualize translation benchmark results."""
    
    def __init__(self, results_path: str):
        """Load results from JSON file.
        
        Args:
            results_path: Path to results JSON file
        """
        with open(results_path, 'r') as f:
            self.results = json.load(f)
    
    def show_examples(self, n: int = 10, sort_by: str = None):
        """Show sample translations.
        
        Args:
            n: Number of examples to show
            sort_by: Optional sorting ('confidence', 'length', None)
        """
        predictions = self.results['predictions'][:n]
        
        print(f"\nSample Translations (first {n}):")
        print("="*80)
        
        for i, pred in enumerate(predictions, 1):
            print(f"\n[Example {i}]")
            print(f"Sumerian:    {pred['sumerian']}")
            print(f"Reference:   {pred['reference']}")
            print(f"Translation: {pred['prediction']}")
            print(f"Confidence:  {pred['metadata']['confidence']}")
            if pred['metadata'].get('notes'):
                print(f"Notes:       {pred['metadata']['notes'][:100]}...")
    
    def error_analysis(self):
        """Analyze common error patterns."""
        predictions = self.results['predictions']
        
        # Count exact matches
        exact_matches = sum(1 for p in predictions if p['prediction'] == p['reference'])
        
        # Analyze by confidence
        by_confidence = {}
        for p in predictions:
            conf = p['metadata']['confidence']
            if conf not in by_confidence:
                by_confidence[conf] = {'count': 0, 'avg_length': 0, 'lengths': []}
            by_confidence[conf]['count'] += 1
            by_confidence[conf]['lengths'].append(len(p['prediction']))
        
        for conf, data in by_confidence.items():
            data['avg_length'] = sum(data['lengths']) / len(data['lengths'])
        
        print(f"\nError Analysis:")
        print(f"  Exact matches: {exact_matches}/{len(predictions)} ({exact_matches/len(predictions)*100:.1f}%)")
        print(f"\n  By confidence:")
        for conf, data in by_confidence.items():
            print(f"    {conf}: {data['count']} examples, avg length: {data['avg_length']:.1f} chars")
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert predictions to pandas DataFrame for analysis.
        
        Returns:
            DataFrame with all prediction data
        """
        rows = []
        for pred in self.results['predictions']:
            rows.append({
                'sumerian': pred['sumerian'],
                'reference': pred['reference'],
                'prediction': pred['prediction'],
                'confidence': pred['metadata']['confidence'],
                'notes': pred['metadata'].get('notes', ''),
                'input_tokens': pred['metadata']['usage']['input_tokens'],
                'output_tokens': pred['metadata']['usage']['output_tokens']
            })
        return pd.DataFrame(rows)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analysis.py <results_json_path>")
        sys.exit(1)
    
    analyzer = ResultsAnalyzer(sys.argv[1])
    
    # Show metrics
    metrics = analyzer.results['metrics']
    print(f"\nBLEU: {metrics['bleu']['score']:.2f}")
    print(f"chrF++: {metrics['chrf']['score']:.2f}")
    
    # Show examples
    analyzer.show_examples(5)
    
    # Error analysis
    analyzer.error_analysis()
    
    # Export to CSV if requested
    if len(sys.argv) > 2 and sys.argv[2] == '--csv':
        df = analyzer.to_dataframe()
        csv_path = Path(sys.argv[1]).with_suffix('.csv')
        df.to_csv(csv_path, index=False)
        print(f"\nExported to: {csv_path}")