#!/bin/bash
# ClayVoices LaTeX compilation and preview script

# Compile LaTeX to PDF
echo "Compiling LaTeX..."
cd "$(dirname "$0")"

# Run pdflatex twice for references
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# Check if compilation succeeded
if [ -f "main.pdf" ]; then
    echo "✓ PDF compiled successfully!"
    
    # Copy to web root for live preview
    mkdir -p /tmp/paper_preview
    cp main.pdf /tmp/paper_preview/clayvoices_paper.pdf
    
    echo "✓ PDF available for preview"
    echo "  File: /tmp/paper_preview/clayvoices_paper.pdf"
else
    echo "✗ PDF compilation failed!"
    exit 1
fi

# Clean up auxiliary files
rm -f *.aux *.log *.bbl *.blg *.out *.toc

echo "Done!"