#!/usr/bin/env python3
"""
Download SumTablets Dataset from Hugging Face

SumTablets: 91,606 Sumerian cuneiform tablets with transliterations
Source: https://huggingface.co/datasets/colesimmons/SumTablets
Paper: https://aclanthology.org/2024.ml4al-1.20/

This dataset pairs Unicode cuneiform glyphs with transliterations, enabling
NLP research on Sumerian texts.
"""

import argparse
from pathlib import Path

try:
    from datasets import load_dataset
except ImportError:
    print("Error: 'datasets' library not installed")
    print("Install with: pip install datasets")
    exit(1)


def download_sumtablets(output_dir: Path, cache_dir: Path = None):
    """
    Download the SumTablets dataset.
    
    Args:
        output_dir: Directory to save the dataset
        cache_dir: Optional cache directory for Hugging Face downloads
    """
    print("=" * 70)
    print("Downloading SumTablets Dataset")
    print("=" * 70)
    print(f"\nSource: https://huggingface.co/datasets/colesimmons/SumTablets")
    print(f"Size: 91,606 tablets | 6.97M glyphs")
    print(f"Output: {output_dir}")
    print()
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download dataset
    print("Downloading from Hugging Face...")
    dataset = load_dataset(
        "colesimmons/SumTablets",
        cache_dir=cache_dir,
    )
    
    print(f"\nDataset loaded successfully!")
    print(f"Splits: {list(dataset.keys())}")
    
    if "train" in dataset:
        print(f"Train split: {len(dataset['train'])} examples")
    
    # Save to disk
    print(f"\nSaving to {output_dir}...")
    dataset.save_to_disk(output_dir)
    
    # Also save as JSON for easy inspection
    json_output = output_dir / "sample_100.json"
    if "train" in dataset:
        sample = dataset["train"].select(range(min(100, len(dataset["train"]))))
        sample.to_json(json_output)
        print(f"Sample (100 tablets) saved to: {json_output}")
    
    print("\n" + "=" * 70)
    print("Download Complete!")
    print("=" * 70)
    print(f"\nDataset saved to: {output_dir}")
    print("\nTo load in Python:")
    print(f"  from datasets import load_from_disk")
    print(f"  dataset = load_from_disk('{output_dir}')")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Download SumTablets dataset from Hugging Face"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("../data/sumtablets"),
        help="Output directory for dataset",
    )
    parser.add_argument(
        "--cache",
        "-c",
        type=Path,
        default=None,
        help="Cache directory for Hugging Face downloads",
    )
    
    args = parser.parse_args()
    download_sumtablets(args.output, args.cache)


if __name__ == "__main__":
    main()