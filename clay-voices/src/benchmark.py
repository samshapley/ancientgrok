import argparse
import json
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import time

from data_loader import ParallelCorpus
from api_clients import ClaudeClient, GPT5Client, GeminiClient
from clients import GrokChatClient
from evaluator import TranslationEvaluator
from prompts import PromptBuilder


class TranslationBenchmark:
    """Orchestrates translation experiments across models and shot settings."""
    
    def __init__(self, data_dir: str = "data", results_dir: str = "results", dataset: str = "sumerian"):
        """Initialize benchmark.
        
        Args:
            data_dir: Directory with parallel data
            results_dir: Directory for results output
            dataset: Which dataset to use ('sumerian' or 'egyptian')
        """
        self.corpus = ParallelCorpus(data_dir, dataset=dataset)
        self.evaluator = TranslationEvaluator()
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.dataset = dataset
        
    def run_experiment(
        self,
        model_name: str,
        n_shot: int,
        test_subset_size: int = None,
        few_shot_seed: int = 42,
        test_seed: int = 99,
        mode: str = "individual",
        system_prompt_variant: str = "default",
        monolingual_base_size: int = 0
    ) -> Dict:
        """Run a single experiment configuration.
        
        Args:
            model_name: Model identifier (e.g., 'claude-sonnet-4-20250514')
            n_shot: Number of few-shot examples (0 for zero-shot)
            test_subset_size: Number of test examples (None = all)
            few_shot_seed: Seed for sampling few-shot examples
            test_seed: Seed for sampling test subset
            mode: 'individual' for streaming or 'batch' for async batch API
            system_prompt_variant: System prompt variant ('default', 'scribe', 'finkel', 'minimal')
            monolingual_base_size: Number of monolingual Sumerian sentences to prepend as context (0 = none)
            
        Returns:
            Results dictionary
        """
        print(f"\n{'='*70}")
        mono_info = f" | mono_base={monolingual_base_size}" if monolingual_base_size > 0 else ""
        print(f"Running: {model_name} | {n_shot}-shot | test_size={test_subset_size or 'all'} | mode={mode} | prompt={system_prompt_variant}{mono_info}")
        print(f"{'='*70}")
        
        # Initialize client based on model name
        if "claude" in model_name.lower():
            client = ClaudeClient(model=model_name)
        elif "gpt" in model_name.lower():
            client = GPT5Client(model=model_name)
        elif "gemini" in model_name.lower():
            client = GeminiClient(model=model_name)
        elif "grok" in model_name.lower():
            client = GrokChatClient(model=model_name)
        else:
            raise NotImplementedError(f"Model {model_name} not supported. Use claude-*/gpt-*/gemini-*/grok-* model names.")
        
        # Get system prompt for this variant
        prompt_builder = None
        
        # Use modular prompt builder for Egyptian
        if self.dataset == "egyptian":
            from prompt_builder import ModularPromptBuilder
            from configs.languages import EGYPTIAN_CONFIG
            from configs.roles import create_expert_role, create_scribe_role, FINKEL_ROLE, MINIMAL_ROLE
            from configs.formats import STANDARD_FORMAT
            
            # Select role based on variant
            if system_prompt_variant == "scribe":
                role = create_scribe_role(EGYPTIAN_CONFIG)
            elif system_prompt_variant == "finkel":
                role = FINKEL_ROLE
            elif system_prompt_variant == "minimal":
                role = MINIMAL_ROLE
            else:  # default
                role = create_expert_role(EGYPTIAN_CONFIG)
            
            prompt_builder = ModularPromptBuilder(EGYPTIAN_CONFIG, role, STANDARD_FORMAT)
            system_prompt = None
        else:
            # Use legacy PromptBuilder for Sumerian
            if system_prompt_variant == "scribe":
                system_prompt = PromptBuilder.SCRIBE_PROMPT
            elif system_prompt_variant == "finkel":
                system_prompt = PromptBuilder.FINKEL_PROMPT
            elif system_prompt_variant == "minimal":
                system_prompt = PromptBuilder.MINIMAL_PROMPT
            else:  # default
                system_prompt = None  # Will use client's default
        
        # Get few-shot examples
        few_shot_examples = self.corpus.sample_few_shot(n_shot, seed=few_shot_seed) if n_shot > 0 else []
        
        # Get monolingual base examples if requested
        monolingual_base = self.corpus.sample_monolingual(monolingual_base_size, seed=few_shot_seed) if monolingual_base_size > 0 else None
        
        # Get test subset
        test_pairs = self.corpus.get_test_subset(test_subset_size, seed=test_seed)
        
        print(f"Test set size: {len(test_pairs)}")
        print(f"Few-shot examples: {len(few_shot_examples)}")
        if monolingual_base:
            print(f"Monolingual base: {len(monolingual_base)} Sumerian sentences")
        print(f"System prompt: {system_prompt_variant}")
        
        # Cost estimation before running
        from cost_tracker import CostTracker
        
        cost_estimate = CostTracker.estimate_cost(
            n_examples=len(test_pairs),
            n_shot=n_shot,
            model=model_name,
            batch_mode=(mode == "batch"),
            monolingual_base_size=monolingual_base_size
        )
        
        print(f"\n💰 Estimated Cost: ${cost_estimate['estimated_cost_usd']:.2f}")
        print(f"   Input tokens: ~{cost_estimate['estimated_input_tokens']:,}")
        print(f"   Output tokens: ~{cost_estimate['estimated_output_tokens']:,}")
        if mode == "batch":
            standard_cost = cost_estimate['estimated_cost_usd'] / 0.5
            print(f"   Batch savings: ${standard_cost - cost_estimate['estimated_cost_usd']:.2f} (50% off)")
        
        predictions = []
        references = []
        metadata = []
        
        if mode == "batch":
            # Batch mode: submit all at once
            sumerian_texts = [pair[0] for pair in test_pairs]
            references = [pair[1] for pair in test_pairs]
            
            try:
                # Only pass prompt_builder to ClaudeClient (which supports it)
                if isinstance(client, ClaudeClient) and prompt_builder is not None:
                    batch_results = client.translate_batch(
                        sumerian_texts,
                        few_shot_examples=few_shot_examples,
                        monolingual_base=monolingual_base,
                        prompt_builder=prompt_builder
                    )
                else:
                    batch_results = client.translate_batch(
                        sumerian_texts,
                        few_shot_examples=few_shot_examples,
                        system_prompt=system_prompt,
                        monolingual_base=monolingual_base
                    )
                
                for result in batch_results:
                    predictions.append(result["translation"])
                    metadata.append(result)
                    
            except Exception as e:
                print(f"\nBatch translation error: {e}")
                # Fill with empty predictions on batch failure
                predictions = [""] * len(test_pairs)
                metadata = [{"translation": "", "confidence": "error", "notes": str(e)}] * len(test_pairs)
        
        else:
            # Individual mode: call API for each example
            for sumerian_text, english_ref in tqdm(test_pairs, desc="Translating"):
                try:
                    # Only pass prompt_builder to ClaudeClient (which supports it)
                    if isinstance(client, ClaudeClient) and prompt_builder is not None:
                        result = client.translate(
                            sumerian_text,
                            few_shot_examples=few_shot_examples,
                            monolingual_base=monolingual_base,
                            prompt_builder=prompt_builder
                        )
                    else:
                        result = client.translate(
                            sumerian_text,
                            few_shot_examples=few_shot_examples,
                            system_prompt=system_prompt,
                            monolingual_base=monolingual_base
                        )
                    
                    predictions.append(result["translation"])
                    metadata.append(result)
                    
                    # Rate limiting - be conservative
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"\nError translating '{sumerian_text}': {e}")
                    predictions.append("")  # Empty prediction on error
                    metadata.append({"translation": "", "confidence": "error", "notes": str(e)})
                
                references.append(english_ref)
        
        # Evaluate
        eval_results = self.evaluator.evaluate(predictions, references, metadata)
        
        # Calculate actual cost
        total_input = sum(m.get("usage", {}).get("input_tokens", 0) for m in metadata)
        total_output = sum(m.get("usage", {}).get("output_tokens", 0) for m in metadata)
        actual_cost = CostTracker.calculate_cost(total_input, total_output, model_name, mode == "batch")
        
        # Add cost to results
        full_results = {
            "experiment": {
                "model": model_name,
                "n_shot": n_shot,
                "test_size": len(test_pairs),
                "few_shot_seed": few_shot_seed,
                "test_seed": test_seed,
                "system_prompt_variant": system_prompt_variant,
                "monolingual_base_size": monolingual_base_size
            },
            "cost": {
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "cost_usd": actual_cost,
                "cost_per_example": actual_cost / len(test_pairs),
                "batch_mode": mode == "batch"
            },
            "metrics": eval_results,
            "predictions": [
                {
                    "sumerian": sum_text,
                    "reference": ref,
                    "prediction": pred,
                    "metadata": meta
                }
                for (sum_text, ref), pred, meta in zip(test_pairs, predictions, metadata)
            ]
        }
        
        # Print results
        self.evaluator.print_results(eval_results)
        
        # Print actual cost
        print(f"\n💰 Actual Cost: ${actual_cost:.2f}")
        print(f"   Input tokens: {total_input:,}")
        print(f"   Output tokens: {total_output:,}")
        print(f"   Accuracy vs estimate: {(actual_cost / cost_estimate['estimated_cost_usd'] * 100):.1f}%")
        
        # Save results with mono base in filename if used
        mono_suffix = f"_mono{monolingual_base_size}" if monolingual_base_size > 0 else ""
        output_file = self.results_dir / f"{model_name.replace('/', '-')}_{n_shot}shot_{system_prompt_variant}{mono_suffix}.json"
        self.evaluator.save_results(full_results, str(output_file))
        print(f"Results saved to: {output_file}")
        
        return full_results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run ancient language translation benchmark")
    parser.add_argument("--model", type=str, default="claude-sonnet-4-20250514",
                       help="Model identifier")
    parser.add_argument("--dataset", type=str, choices=["sumerian", "egyptian"], default="sumerian",
                       help="Which dataset to use: 'sumerian' (default) or 'egyptian'")
    parser.add_argument("--shots", type=int, nargs="+", default=[0, 1, 3, 5],
                       help="Number of few-shot examples to test")
    parser.add_argument("--test-size", type=int, default=None,
                       help="Test subset size (None = all)")
    parser.add_argument("--data-dir", type=str, default="data",
                       help="Data directory")
    parser.add_argument("--results-dir", type=str, default="results",
                       help="Results output directory")
    parser.add_argument("--mode", type=str, choices=["individual", "batch"], default="individual",
                       help="API mode: 'individual' for streaming calls, 'batch' for async batch API (50%% cost savings)")
    parser.add_argument("--prompt-variant", type=str, choices=["default", "scribe", "finkel", "minimal"], default="default",
                       help="System prompt variant: 'default', 'scribe' (Sumerian scribe persona), 'finkel' (Irving Finkel persona), 'minimal' (no system prompt)")
    parser.add_argument("--monolingual-base-size", type=int, default=0,
                       help="Number of monolingual Sumerian sentences to prepend as context priming (0 = none, only works with Sumerian dataset)")
    
    args = parser.parse_args()
    
    # Initialize benchmark with selected dataset
    benchmark = TranslationBenchmark(args.data_dir, args.results_dir, dataset=args.dataset)
    
    print(f"\nDataset Statistics:")
    print(json.dumps(benchmark.corpus.stats(), indent=2))
    
    # Run experiments for each shot setting
    all_results = []
    for n_shot in args.shots:
        result = benchmark.run_experiment(
            model_name=args.model,
            n_shot=n_shot,
            test_subset_size=args.test_size,
            mode=args.mode,
            system_prompt_variant=args.prompt_variant,
            monolingual_base_size=args.monolingual_base_size
        )
        all_results.append(result)
    
    # Save summary
    mono_suffix = f"_mono{args.monolingual_base_size}" if args.monolingual_base_size > 0 else ""
    summary_file = benchmark.results_dir / f"summary_{args.model.replace('/', '-')}_{args.prompt_variant}{mono_suffix}.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "model": args.model,
            "prompt_variant": args.prompt_variant,
            "monolingual_base_size": args.monolingual_base_size,
            "experiments": all_results
        }, f, indent=2)
    
    print(f"\nAll experiments complete. Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()