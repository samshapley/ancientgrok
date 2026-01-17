#!/usr/bin/env python3
"""
Download CuneiML Dataset from Zenodo

CuneiML: 38,947 high-resolution photographs of Sumerian/Akkadian tablets
Source: https://zenodo.org/records/10806319
Paper: https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.151

This dataset provides tablet images with transcriptions for computer vision
and OCR research on cuneiform.
"""

import argparse
import shutil
import zipfile
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: 'httpx' library not installed")
    print("Install with: pip install httpx")
    exit(1)


def download_cuneiml(output_dir: Path, download_images: bool = False):
    """
    Download the CuneiML dataset.
    
    Args:
        output_dir: Directory to save the dataset
        download_images: Whether to download the full image dataset (~50GB)
    """
    print("=" * 70)
    print("CuneiML Dataset Download")
    print("=" * 70)
    print(f"\nSource: https://zenodo.org/records/10806319")
    print(f"Size: 38,947 tablet photographs")
    print(f"Output: {output_dir}")
    
    if not download_images:
        print("\n⚠️  WARNING: Full image dataset is ~50GB")
        print("Use --images flag to download images")
        print("Downloading metadata only...")
    print()
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Zenodo record ID for CuneiML
    record_id = "10806319"
    metadata_url = f"https://zenodo.org/api/records/{record_id}"
    
    print("Fetching dataset metadata...")
    with httpx.Client(timeout=30.0) as client:
        response = client.get(metadata_url)
        if response.status_code != 200:
            print(f"Error: Could not fetch metadata (HTTP {response.status_code})")
            return
        
        metadata = response.json()
        
        # Save metadata
        import json
        metadata_file = output_dir / "metadata.json"
        with metadata_file.open("w") as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to: {metadata_file}")
        
        # Get file information
        files = metadata.get("files", [])
        print(f"\nDataset files ({len(files)}):")
        
        total_size = 0
        for file_info in files:
            filename = file_info.get("key", "unknown")
            size_mb = file_info.get("size", 0) / (1024 * 1024)
            total_size += size_mb
            print(f"  - {filename}: {size_mb:.1f} MB")
        
        print(f"\nTotal size: {total_size / 1024:.2f} GB")
        
        if download_images and files:
            print("\nDownloading files...")
            for file_info in files:
                filename = file_info.get("key")
                file_url = file_info.get("links", {}).get("self")
                
                if not file_url:
                    continue
                
                output_file = output_dir / filename
                
                if output_file.exists():
                    print(f"  ✓ {filename} (already exists)")
                    continue
                
                print(f"  Downloading {filename}...")
                with client.stream("GET", file_url) as stream:
                    stream.raise_for_status()
                    with output_file.open("wb") as f:
                        for chunk in stream.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                
                # Extract if ZIP
                if filename.endswith(".zip"):
                    print(f"  Extracting {filename}...")
                    with zipfile.ZipFile(output_file, 'r') as zip_ref:
                        zip_ref.extractall(output_dir)
                    output_file.unlink()  # Remove ZIP after extraction
                
                print(f"  ✓ {filename} downloaded")
        else:
            print("\nTo download full dataset (images), run with --images flag")
    
    print("\n" + "=" * 70)
    print("Download Complete!")
    print("=" * 70)
    print(f"\nDataset information saved to: {output_dir}")
    print("\nCitation:")
    print("  Taineleau et al. (2024). CuneiML: A Cuneiform Dataset for")
    print("  Machine Learning. Journal of Open Humanities Data.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Download CuneiML dataset from Zenodo"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("../data/cuneiml"),
        help="Output directory for dataset",
    )
    parser.add_argument(
        "--images",
        action="store_true",
        help="Download full image dataset (~50GB)",
    )
    
    args = parser.parse_args()
    download_cuneiml(args.output, args.images)


if __name__ == "__main__":
    main()