#!/bin/bash
# AncientGrok Demonstration Script
# Shows all capabilities of the interactive ancient world knowledge agent

cat << 'EOF' | ancientgrok

# 1. Show help
help

# 2. Simple historical question
Who ruled Babylon during the Old Babylonian period?

# 3. CDLI database query
Search CDLI for Old Babylonian tablets from Babylon

# 4. List historical periods
List all CDLI periods

# 5. Computational question
Calculate 60 times 60 (Mesopotamian sexagesimal base)

# 6. Get specific tablet details
Get details for tablet P142661

# 7. Current research question
What are recent discoveries about Hammurabi's code?

# 8. Show available tools
tools

# 9. Exit
exit

EOF

echo "AncientGrok demonstration complete!"