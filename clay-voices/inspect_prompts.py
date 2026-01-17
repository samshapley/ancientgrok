"""Prompt inspection and demo utility for rapid iteration without API costs.

Enables testing prompt variations, estimating costs, and comparing configurations
before running expensive benchmark experiments.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, 'src')

from prompt_builder import ModularPromptBuilder
from configs.languages import SUMERIAN_CONFIG, EGYPTIAN_CONFIG
from configs.roles import create_expert_role, create_scribe_role, FINKEL_ROLE, MINIMAL_ROLE
from configs.formats import STANDARD_FORMAT, INLINE_FORMAT, COT_FORMAT
from data_loader import ParallelCorpus
from cost_tracker import CostTracker


def get_config_by_name(config_type: str, name: str):
    """Get configuration object by type and name.
    
    Args:
        config_type: 'language', 'role', or 'format'
        name: Configuration name
        
    Returns:
        Configuration object
        
    Raises:
        ValueError: If configuration name is unknown
    """
    if config_type == "language":
        lang_map = {"sumerian": SUMERIAN_CONFIG, "egyptian": EGYPTIAN_CONFIG}
        if name not in lang_map:
            raise ValueError(f"Unknown language: {name}. Choose from: {', '.join(lang_map.keys())}")
        return lang_map[name]
    
    elif config_type == "role":
        if name == "expert":
            lang = SUMERIAN_CONFIG
            return create_expert_role(lang)
        elif name == "scribe":
            lang = SUMERIAN_CONFIG
            return create_scribe_role(lang)
        elif name == "finkel":
            return FINKEL_ROLE
        elif name == "minimal":
            return MINIMAL_ROLE
        else:
            raise ValueError(f"Unknown role: {name}. Choose from: expert, scribe, finkel, minimal")
    
    elif config_type == "format":
        fmt_map = {"standard": STANDARD_FORMAT, "inline": INLINE_FORMAT, "cot": COT_FORMAT}
        if name not in fmt_map:
            raise ValueError(f"Unknown format: {name}. Choose from: {', '.join(fmt_map.keys())}")
        return fmt_map[name]
    
    raise ValueError(f"Unknown config_type: {config_type}")


def estimate_tokens(text: str) -> int:
    """Rough token count estimation."""
    words = len(text.split())
    return int(words * 1.3)


def show_prompt(
    language: str = "egyptian",
    role: str = "expert",
    format_name: str = "standard",
    n_shot: int = 10,
    monolingual_base: int = 0,
    test_index: int = 0,
    export_path: str = None
):
    """Generate and display a sample prompt."""
    
    # Load data with specific error handling
    try:
        corpus = ParallelCorpus("data", dataset=language)
    except FileNotFoundError as e:
        print(f"Error: Could not load {language} dataset: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate test_index
    if test_index >= len(corpus.test_pairs) or test_index < 0:
        print(f"Error: test_index {test_index} out of range (0-{len(corpus.test_pairs)-1})", file=sys.stderr)
        sys.exit(1)
    
    # Get configurations with specific error handling
    try:
        lang_config = get_config_by_name("language", language)
        
        if role == "expert":
            role_config = create_expert_role(lang_config)
        elif role == "scribe":
            role_config = create_scribe_role(lang_config)
        else:
            role_config = get_config_by_name("role", role)
        
        format_config = get_config_by_name("format", format_name)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Build prompt
    builder = ModularPromptBuilder(lang_config, role_config, format_config)
    
    few_shot = corpus.sample_few_shot(n_shot) if n_shot > 0 else []
    mono = corpus.sample_monolingual(monolingual_base) if monolingual_base > 0 else None
    
    test_text, test_translation = corpus.test_pairs[test_index]
    
    system, user = builder.build(test_text, few_shot, mono)
    
    # Display
    print("="*80)
    print(f"PROMPT DEMO: {language.upper()} | {role} role | {format_name} format | {n_shot}-shot")
    if monolingual_base > 0:
        print(f"             + {monolingual_base} monolingual base")
    print("="*80)
    
    print("\n--- SYSTEM PROMPT ---")
    print(system)
    
    print("\n--- USER PROMPT ---")
    if len(user) > 2000:
        print(user[:2000])
        print(f"\n... [truncated, showing first 2000 of {len(user)} characters]")
    else:
        print(user)
    
    # Token estimates
    system_tokens = estimate_tokens(system)
    user_tokens = estimate_tokens(user)
    total_tokens = system_tokens + user_tokens
    
    print(f"\n--- TOKEN & COST ESTIMATE ---")
    print(f"System prompt: ~{system_tokens:,} tokens")
    print(f"User prompt: ~{user_tokens:,} tokens")
    print(f"Total per request: ~{total_tokens:,} tokens")
    
    cost_est = CostTracker.estimate_cost(
        n_examples=200,
        n_shot=n_shot,
        model="claude-opus-4-5-20251101",
        batch_mode=True,
        monolingual_base_size=monolingual_base
    )
    print(f"\nFor 200-example benchmark:")
    print(f"  Estimated cost: ${cost_est['estimated_cost_usd']:.2f} (batch mode)")
    print(f"  Total tokens: ~{cost_est['estimated_total_tokens']:,}")
    
    print(f"\n--- TEST EXAMPLE ---")
    print(f"Source: {test_text}")
    print(f"Reference: {test_translation}")
    
    # Export with file error handling
    if export_path:
        try:
            Path(export_path).parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, 'w') as f:
                f.write(f"SYSTEM PROMPT:\n{system}\n\n")
                f.write(f"USER PROMPT:\n{user}\n\n")
                f.write(f"TEST: {test_text}\n")
                f.write(f"REFERENCE: {test_translation}\n")
            print(f"\n✓ Exported to: {export_path}")
        except (OSError, IOError) as e:
            print(f"Error: Could not export to {export_path}: {e}", file=sys.stderr)
            sys.exit(1)
    
    return system, user


def compare_roles(language: str = "egyptian", n_shot: int = 10):
    """Compare all role variants for a language."""
    print("="*80)
    print(f"ROLE COMPARISON: {language.upper()} | {n_shot}-shot")
    print("="*80)
    
    for role in ["expert", "scribe", "finkel", "minimal"]:
        print(f"\n--- {role.upper()} ROLE ---")
        show_prompt(language, role, "standard", n_shot)
        print(f"\n{'-'*80}\n")


def compare_formats(language: str = "egyptian", role: str = "expert", n_shot: int = 10):
    """Compare all format variants."""
    print("="*80)
    print(f"FORMAT COMPARISON: {language.upper()} | {role} role | {n_shot}-shot")
    print("="*80)
    
    for fmt in ["standard", "inline", "cot"]:
        _, user = show_prompt(language, role, fmt, n_shot)
        print(f"\n{fmt.upper()} FORMAT (user prompt preview):")
        print(user[:500] + "..." if len(user) > 500 else user)
        print(f"\n{'-'*80}\n")


def main():
    """Main entry point with CLI."""
    parser = argparse.ArgumentParser(
        description="Inspect and demo ClayVoices prompts without running API calls"
    )
    
    parser.add_argument("--language", type=str, choices=["sumerian", "egyptian"], default="egyptian",
                       help="Ancient language to demo")
    parser.add_argument("--role", type=str, choices=["expert", "scribe", "finkel", "minimal"], default="expert",
                       help="Role/persona variant")
    parser.add_argument("--format", type=str, choices=["standard", "inline", "cot"], default="standard",
                       help="Prompt format structure")
    parser.add_argument("--shots", type=int, default=10,
                       help="Number of few-shot examples")
    parser.add_argument("--monolingual-base", type=int, default=0,
                       help="Number of monolingual sentences (Sumerian only)")
    parser.add_argument("--test-index", type=int, default=0,
                       help="Which test example to use (0-based)")
    parser.add_argument("--export", type=str, default=None,
                       help="Export prompt to file")
    parser.add_argument("--compare-roles", action="store_true",
                       help="Compare all role variants")
    parser.add_argument("--compare-formats", action="store_true",
                       help="Compare all format variants")
    
    args = parser.parse_args()
    
    # Execute requested operation with proper error handling
    try:
        if args.compare_roles:
            compare_roles(args.language, args.shots)
        elif args.compare_formats:
            compare_formats(args.language, args.role, args.shots)
        else:
            show_prompt(
                language=args.language,
                role=args.role,
                format_name=args.format,
                n_shot=args.shots,
                monolingual_base=args.monolingual_base,
                test_index=args.test_index,
                export_path=args.export
            )
    except (ValueError, FileNotFoundError, IndexError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()