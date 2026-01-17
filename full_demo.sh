#!/bin/bash
# Complete AncientGrok capabilities demonstration

cat << 'EOF' | ancientgrok

# Test 1: Help command
help

# Test 2: Historical knowledge
Who was Hammurabi?

# Test 3: CDLI search
Search CDLI for Ur III administrative tablets

# Test 4: List CDLI periods
List all CDLI historical periods

# Test 5: Image generation
Generate an image of the Ishtar Gate

# Test 6: Computational
Calculate 60 factorial

# Test 7: Current research (web search)
What are the latest 2024 discoveries in Mesopotamian archaeology?

# Test 8: Exit
exit

EOF

echo "Demo complete!"
echo "Generated images in:"
ls -lh /tmp/ancientgrok_images/ 2>/dev/null || echo "No images yet"
