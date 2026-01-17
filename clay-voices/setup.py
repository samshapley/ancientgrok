"""Setup script for ClayVoices package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="clayvoices",
    version="0.1.0",
    author="ClayVoices Research Team",
    description="LLM translation benchmark for ancient Sumerian cuneiform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/clayvoices",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.75.0",
        "openai>=1.58.0",
        "google-genai>=0.3.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "sacrebleu>=2.4.0",
        "bert-score>=0.3.13",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
        "pydantic>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "clayvoices=benchmark:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)