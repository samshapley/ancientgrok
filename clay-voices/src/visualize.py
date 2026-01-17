"""Visualization utilities for translation benchmark results."""

import json
from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns


class LearningCurveVisualizer:
    """Visualize learning curves from benchmark results."""
    
    def __init__(self, results_dir: str = "results"):
        """Initialize visualizer.
        
        Args:
            results_dir: Directory containing result JSON files
        """
        self.results_dir = Path(results_dir)
        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=1.2)
    
    def load_results(self, model_name: str) -> List[Dict]:
        """Load all results for a given model.
        
        Args:
            model_name: Model identifier (e.g., 'claude-sonnet-4-20250514')
            
        Returns:
            List of result dictionaries sorted by shot count
        """
        pattern = f"{model_name.replace('/', '-')}_*shot.json"
        result_files = sorted(self.results_dir.glob(pattern),
                            key=lambda p: int(p.stem.split('_')[-1].replace('shot', '')))
        
        results = []
        for file_path in result_files:
            with open(file_path, 'r') as f:
                results.append(json.load(f))
        
        return results
    
    def plot_learning_curve(
        self,
        model_name: str,
        output_path: str = None,
        metrics: List[str] = ["bleu", "chrf"]
    ):
        """Plot BLEU and chrF++ learning curves.
        
        Args:
            model_name: Model to plot
            output_path: Optional path to save figure
            metrics: List of metrics to plot
        """
        results = self.load_results(model_name)
        
        if not results:
            print(f"No results found for model: {model_name}")
            return
        
        # Extract data
        shot_counts = [r["experiment"]["n_shot"] for r in results]
        bleu_scores = [r["metrics"]["bleu"]["score"] for r in results]
        chrf_scores = [r["metrics"]["chrf"]["score"] for r in results]
        
        # Create figure
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # BLEU plot
        axes[0].plot(shot_counts, bleu_scores, 'o-', linewidth=2, markersize=8, label='Claude Sonnet 4')
        axes[0].axhline(y=21.6, color='r', linestyle='--', label='OpenNMT Baseline (21.6)')
        axes[0].set_xlabel('Number of Few-Shot Examples')
        axes[0].set_ylabel('BLEU Score')
        axes[0].set_title('BLEU Learning Curve for Sumerian→English Translation')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # chrF++ plot
        axes[1].plot(shot_counts, chrf_scores, 's-', linewidth=2, markersize=8, 
                    color='green', label='Claude Sonnet 4')
        axes[1].set_xlabel('Number of Few-Shot Examples')
        axes[1].set_ylabel('chrF++ Score')
        axes[1].set_title('chrF++ Learning Curve for Sumerian→English Translation')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to: {output_path}")
        else:
            plt.show()
    
    def plot_confidence_distribution(self, model_name: str, output_path: str = None):
        """Plot how confidence changes with shot count.
        
        Args:
            model_name: Model to plot
            output_path: Optional path to save figure
        """
        results = self.load_results(model_name)
        
        shot_counts = [r["experiment"]["n_shot"] for r in results]
        high_conf = [r["metrics"]["confidence_distribution"].get("high", 0) / 
                    r["metrics"]["num_examples"] * 100 for r in results]
        medium_conf = [r["metrics"]["confidence_distribution"].get("medium", 0) / 
                      r["metrics"]["num_examples"] * 100 for r in results]
        low_conf = [r["metrics"]["confidence_distribution"].get("low", 0) / 
                   r["metrics"]["num_examples"] * 100 for r in results]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(shot_counts, high_conf, 'o-', label='High', linewidth=2, markersize=6)
        ax.plot(shot_counts, medium_conf, 's-', label='Medium', linewidth=2, markersize=6)
        ax.plot(shot_counts, low_conf, '^-', label='Low', linewidth=2, markersize=6)
        
        ax.set_xlabel('Number of Few-Shot Examples')
        ax.set_ylabel('Percentage of Translations (%)')
        ax.set_title('Model Confidence Distribution vs. Few-Shot Examples')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to: {output_path}")
        else:
            plt.show()
    
    def create_results_table(self, model_name: str, output_path: str = None):
        """Create markdown table of results.
        
        Args:
            model_name: Model to summarize
            output_path: Optional path to save markdown table
        """
        results = self.load_results(model_name)
        
        lines = ["# Learning Curve Results\n"]
        lines.append(f"**Model:** {model_name}\n")
        lines.append("| Shot Count | BLEU | chrF++ | BP | High Conf % | Test Size |")
        lines.append("|------------|------|--------|-----|-------------|-----------|")
        
        for r in results:
            n_shot = r["experiment"]["n_shot"]
            bleu = r["metrics"]["bleu"]["score"]
            chrf = r["metrics"]["chrf"]["score"]
            bp = r["metrics"]["bleu"]["bp"]
            high_pct = r["metrics"]["confidence_distribution"].get("high", 0) / r["metrics"]["num_examples"] * 100
            test_size = r["metrics"]["num_examples"]
            
            lines.append(f"| {n_shot} | {bleu:.2f} | {chrf:.2f} | {bp:.2f} | {high_pct:.1f}% | {test_size} |")
        
        table = "\n".join(lines)
        
        if output_path:
            Path(output_path).write_text(table)
            print(f"Table saved to: {output_path}")
        else:
            print(table)
        
        return table


if __name__ == "__main__":
    import sys
    
    model = sys.argv[1] if len(sys.argv) > 1 else "claude-sonnet-4-20250514"
    
    viz = LearningCurveVisualizer()
    
    # Generate table
    print("\n" + "="*70)
    viz.create_results_table(model)
    
    # Generate plots
    print("\n" + "="*70)
    print("Generating plots...")
    viz.plot_learning_curve(model, output_path=f"results/{model.replace('/', '-')}_learning_curve.png")
    viz.plot_confidence_distribution(model, output_path=f"results/{model.replace('/', '-')}_confidence.png")
    
    print("\n✅ Visualization complete!")