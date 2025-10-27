# PowerShell script to add React type references to all .tsx files
# This fixes JSX.IntrinsicElements type errors

Write-Host "Adding React type references to all .tsx files..." -ForegroundColor Green

$reference = '/// <reference types="react" />'

# Find all .tsx files recursively
Get-ChildItem -Path ".\src" -Filter "*.tsx" -Recurse | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content $file -Raw

    # Check if reference already exists
    if ($content -notmatch [regex]::Escape($reference)) {
        Write-Host "Adding reference to: $($_.Name)" -ForegroundColor Yellow

        # Add reference at the beginning
        $newContent = $reference + "`n" + $content
        Set-Content -Path $file -Value $newContent -NoNewline
    }
    else {
        Write-Host "Skipping (already has reference): $($_.Name)" -ForegroundColor Gray
    }
}

Write-Host "`nDone! All .tsx files have been updated." -ForegroundColor Green
Write-Host "Please run: npm run build or npx tsc --noEmit to verify." -ForegroundColor Cyan
