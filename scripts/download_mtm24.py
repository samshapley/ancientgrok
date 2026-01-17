#!/usr/bin/env python3
"""
Download MTM24 Akkadian Cuneiform Transliteration Dataset

MTM24: 1,154,023 lines of Akkadian cuneiform transliteration
Source: https://www.kaggle.com/datasets/manwithacat/mtm24-akkadian-transliteration
Format: Cuneiform signs → scholarly transliteration

Requires Kaggle API credentials configured.
"""

import argparse
import subprocess
from pathlib import Path


def check_kaggle_setup():
    """Check if Kaggle API is set up."""
    try:
        result = subprocess.run(
            ["kaggle", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def download_mtm24(output_dir: Path):
    """
    Download the MTM24 Akkadian dataset.
    
    Args:
        output_dir: Directory to save the dataset
    """
    print("=" * 70)
    print("MTM24 Akkadian Transliteration Dataset")
    print("=" * 70)
    print(f"\nSource: Kaggle - manwithacat/mtm24-akkadian-transliteration")
    print(f"Size: 1,154,023 lines of Akkadian text")
    print(f"Output: {output_dir}")
    print()
    
    # Check Kaggle setup
    if not check_kaggle_setup():
        print("❌ Kaggle CLI not found or not configured")
        print("\nSetup instructions:")
        print("1. Install: pip install kaggle")
        print("2. Get API token from https://www.kaggle.com/settings")
        print("3. Place in ~/.kaggle/kaggle.json")
        print("   Format: {\"username\":\"your_username\",\"key\":\"your_api_key\"}")
        return
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download using Kaggle API
    print("Downloading from Kaggle...")
    result = subprocess.run(
        [
            "kaggle",
            "datasets",
            "download",
            "-d",
            "manwithacat/mtm24-akkadian-transliteration",
            "-p",
            str(output_dir),
            "--unzip",
        ],
        check=False,
    )
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("Download Complete!")
        print("=" * 70)
        print(f"\nDataset saved to: {output_dir}")
        
        # List downloaded files
        files = list(output_dir.glob("*"))
        print(f"\nFiles ({len(files)}):")
        for file in sorted(files)[:10]:
            size_mb = file.stat().st_size / (1024 * 1024) if file.is_file() else 0
            print(f"  - {file.name}: {size_mb:.1f} MB")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")
        
        print("\nUse Case:")
        print("  This dataset is ideal for training transliteration models")
        print("  (cuneiform signs → romanized text)")
        print()
    else:
        print(f"\n❌ Download failed (exit code {result.returncode})")
        print("Check your Kaggle API credentials")


def main():
    parser = argparse.ArgumentParser(
        description="Download MTM24 Akkadian dataset from Kaggle"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("../data/mtm24"),
        help="Output directory for dataset",
    )
    
    args = parser.parse_args()
    download_mtm24(args.output)


if __name__ == "__main__":
    main()