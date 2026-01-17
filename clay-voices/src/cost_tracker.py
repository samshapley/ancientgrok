"""Cost tracking and estimation for LLM translation experiments."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ModelPricing:
    """Pricing information for a model."""
    input_cost_per_million: float  # Cost per 1M input tokens
    output_cost_per_million: float  # Cost per 1M output tokens
    batch_discount: float = 0.5  # Batch API discount (50% by default)


# Model pricing catalog (as of December 2025)
MODEL_PRICING = {
    "claude-sonnet-4-20250514": ModelPricing(3.0, 15.0),
    "claude-opus-4-5-20251101": ModelPricing(5.0, 25.0),
    "claude-haiku-4.5": ModelPricing(1.0, 5.0),
    "gpt-5.2-instant": ModelPricing(2.0, 10.0),
    "gpt-5.2-thinking": ModelPricing(5.0, 15.0),
    "gpt-5.2-pro": ModelPricing(10.0, 30.0),
    "gemini-3-pro-preview": ModelPricing(1.25, 5.0),
    "gemini-2.5-pro": ModelPricing(1.25, 5.0),
    "gemini-2.5-flash": ModelPricing(0.075, 0.3),
}


class CostTracker:
    """Track and report costs for translation experiments."""
    
    @staticmethod
    def calculate_cost(
        input_tokens: int,
        output_tokens: int,
        model: str,
        batch_mode: bool = False
    ) -> float:
        """Calculate cost for a single experiment.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier
            batch_mode: Whether batch API was used
            
        Returns:
            Cost in USD
        """
        if model not in MODEL_PRICING:
            print(f"Warning: Unknown model {model}, using Claude Sonnet 4 pricing")
            pricing = MODEL_PRICING["claude-sonnet-4-20250514"]
        else:
            pricing = MODEL_PRICING[model]
        
        # Calculate base costs
        input_cost = (input_tokens / 1_000_000) * pricing.input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * pricing.output_cost_per_million
        
        # Apply batch discount if applicable
        if batch_mode:
            input_cost *= pricing.batch_discount
            output_cost *= pricing.batch_discount
        
        return input_cost + output_cost
    
    @staticmethod
    def analyze_results_file(results_path: str) -> Dict:
        """Analyze a results JSON file and calculate costs.
        
        Args:
            results_path: Path to results JSON file
            
        Returns:
            Dictionary with cost analysis
        """
        with open(results_path, 'r') as f:
            data = json.load(f)
        
        experiment = data.get("experiment", {})
        predictions = data.get("predictions", [])
        
        # Extract token usage
        total_input = sum(p.get("metadata", {}).get("usage", {}).get("input_tokens", 0) 
                         for p in predictions)
        total_output = sum(p.get("metadata", {}).get("usage", {}).get("output_tokens", 0) 
                          for p in predictions)
        
        # Determine if batch mode (heuristic: check filename or metadata)
        batch_mode = "batch" in str(results_path) or experiment.get("mode") == "batch"
        
        # Calculate cost
        model = experiment.get("model", "claude-sonnet-4-20250514")
        cost = CostTracker.calculate_cost(total_input, total_output, model, batch_mode)
        
        return {
            "file": str(results_path),
            "model": model,
            "n_shot": experiment.get("n_shot", 0),
            "test_size": experiment.get("test_size", len(predictions)),
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "batch_mode": batch_mode,
            "cost_usd": cost,
            "cost_per_example": cost / len(predictions) if predictions else 0
        }
    
    @staticmethod
    def analyze_directory(results_dir: str = "results") -> List[Dict]:
        """Analyze all results files in a directory.
        
        Args:
            results_dir: Directory containing results JSON files
            
        Returns:
            List of cost analyses sorted by cost
        """
        results_path = Path(results_dir)
        analyses = []
        
        for json_file in results_path.glob("*.json"):
            if "summary" not in json_file.name:  # Skip summary files
                try:
                    analysis = CostTracker.analyze_results_file(str(json_file))
                    analyses.append(analysis)
                except Exception as e:
                    print(f"Error analyzing {json_file.name}: {e}")
        
        # Sort by cost descending
        analyses.sort(key=lambda x: x["cost_usd"], reverse=True)
        
        return analyses
    
    @staticmethod
    def estimate_cost(
        n_examples: int,
        n_shot: int,
        model: str,
        batch_mode: bool = True,
        avg_source_tokens: int = 15,
        avg_target_tokens: int = 150,
        system_prompt_tokens: int = 250,
        monolingual_base_size: int = 0,
        avg_monolingual_tokens: int = 10
    ) -> Dict:
        """Estimate cost for a planned experiment.
        
        Args:
            n_examples: Number of test examples to translate
            n_shot: Number of few-shot examples
            model: Model identifier
            batch_mode: Whether to use batch API
            avg_source_tokens: Average tokens per source sentence
            avg_target_tokens: Average tokens per target sentence
            system_prompt_tokens: Tokens in system prompt
            monolingual_base_size: Number of monolingual sentences
            avg_monolingual_tokens: Average tokens per monolingual sentence
            
        Returns:
            Cost estimation dictionary
        """
        # Estimate input tokens per request
        # System prompt + few-shot examples + monolingual base + test sentence
        few_shot_tokens = n_shot * (avg_source_tokens + avg_target_tokens + 20)  # +20 for formatting
        mono_tokens = monolingual_base_size * (avg_monolingual_tokens + 5)
        per_request_input = system_prompt_tokens + few_shot_tokens + mono_tokens + avg_source_tokens
        
        total_input = per_request_input * n_examples
        total_output = avg_target_tokens * n_examples  # Estimate
        
        cost = CostTracker.calculate_cost(total_input, total_output, model, batch_mode)
        
        return {
            "n_examples": n_examples,
            "n_shot": n_shot,
            "model": model,
            "batch_mode": batch_mode,
            "monolingual_base_size": monolingual_base_size,
            "estimated_input_tokens": total_input,
            "estimated_output_tokens": total_output,
            "estimated_total_tokens": total_input + total_output,
            "estimated_cost_usd": cost,
            "cost_per_example": cost / n_examples
        }
    
    @staticmethod
    def print_cost_report(analyses: List[Dict], show_top_n: int = 10):
        """Print a formatted cost report.
        
        Args:
            analyses: List of cost analyses
            show_top_n: Number of top experiments to show
        """
        if not analyses:
            print("No cost data available.")
            return
        
        total_cost = sum(a["cost_usd"] for a in analyses)
        total_tokens = sum(a["total_tokens"] for a in analyses)
        
        print(f"\n{'='*80}")
        print("CLAYVOICES COST REPORT")
        print(f"{'='*80}")
        print(f"Total experiments: {len(analyses)}")
        print(f"Total cost: ${total_cost:.2f}")
        print(f"Total tokens: {total_tokens:,}")
        print(f"Average cost per experiment: ${total_cost / len(analyses):.2f}")
        
        print(f"\nTop {min(show_top_n, len(analyses))} Most Expensive Experiments:")
        print(f"{'File':<60} {'Cost':>10} {'Tokens':>12} {'Mode':>6}")
        print("-" * 80)
        
        for i, analysis in enumerate(analyses[:show_top_n], 1):
            filename = Path(analysis["file"]).name
            mode = "batch" if analysis["batch_mode"] else "indiv"
            print(f"{filename:<60} ${analysis['cost_usd']:>9.2f} {analysis['total_tokens']:>12,} {mode:>6}")
        
        # Breakdown by model
        by_model = {}
        for a in analyses:
            model = a["model"]
            if model not in by_model:
                by_model[model] = {"cost": 0, "count": 0}
            by_model[model]["cost"] += a["cost_usd"]
            by_model[model]["count"] += 1
        
        print(f"\nCost by Model:")
        for model, info in sorted(by_model.items(), key=lambda x: x[1]["cost"], reverse=True):
            print(f"  {model}: ${info['cost']:.2f} ({info['count']} experiments)")
        
        print(f"{'='*80}\n")
    
    @staticmethod
    def print_cost_estimate(estimate: Dict):
        """Print a formatted cost estimate.
        
        Args:
            estimate: Cost estimation dictionary
        """
        print(f"\n{'='*70}")
        print("COST ESTIMATE")
        print(f"{'='*70}")
        print(f"Configuration:")
        print(f"  Model: {estimate['model']}")
        print(f"  Test examples: {estimate['n_examples']}")
        print(f"  Few-shot examples: {estimate['n_shot']}")
        if estimate['monolingual_base_size'] > 0:
            print(f"  Monolingual base: {estimate['monolingual_base_size']} sentences")
        print(f"  Mode: {'Batch (50% discount)' if estimate['batch_mode'] else 'Individual (standard pricing)'}")
        
        print(f"\nEstimated Token Usage:")
        print(f"  Input tokens:  {estimate['estimated_input_tokens']:>12,}")
        print(f"  Output tokens: {estimate['estimated_output_tokens']:>12,}")
        print(f"  Total tokens:  {estimate['estimated_total_tokens']:>12,}")
        
        print(f"\nEstimated Cost: ${estimate['estimated_cost_usd']:.2f}")
        print(f"  Cost per example: ${estimate['cost_per_example']:.4f}")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python cost_tracker.py analyze [results_dir]  - Analyze completed experiments")
        print("  python cost_tracker.py estimate <args>         - Estimate cost for planned experiment")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        results_dir = sys.argv[2] if len(sys.argv) > 2 else "results"
        analyses = CostTracker.analyze_directory(results_dir)
        CostTracker.print_cost_report(analyses)
        
        # Save detailed report
        with open("cost_report.json", 'w') as f:
            json.dump({
                "total_cost": sum(a["cost_usd"] for a in analyses),
                "total_experiments": len(analyses),
                "experiments": analyses
            }, f, indent=2)
        print(f"Detailed report saved to: cost_report.json")
    
    elif command == "estimate":
        print("Interactive cost estimator - provide parameters")
        # Simple interactive estimator
        n_examples = int(input("Number of test examples: "))
        n_shot = int(input("Number of few-shot examples: "))
        model = input("Model (default: claude-opus-4-5-20251101): ") or "claude-opus-4-5-20251101"
        batch = input("Use batch mode? (y/n, default: y): ").lower() != 'n'
        
        estimate = CostTracker.estimate_cost(n_examples, n_shot, model, batch)
        CostTracker.print_cost_estimate(estimate)