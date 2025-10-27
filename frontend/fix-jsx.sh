#!/bin/bash

# Script to add React type references to all .tsx files
# This fixes JSX.IntrinsicElements type errors

echo "Adding React type references to all .tsx files..."

# Find all .tsx files and add reference types if not already present
find src -name "*.tsx" -type f | while read file; do
    # Check if the file already has the reference
    if ! grep -q "/// <reference types=\"react\" />" "$file"; then
        # Add the reference at the beginning of the file
        echo "Adding reference to: $file"

        # Create temp file with reference
        echo '/// <reference types="react" />' > temp_file
        cat "$file" >> temp_file

        # Replace original file
        mv temp_file "$file"
    else
        echo "Skipping (already has reference): $file"
    fi
done

echo "Done! All .tsx files have been updated."
echo "Please run: npm run build or npx tsc --noEmit to verify."
