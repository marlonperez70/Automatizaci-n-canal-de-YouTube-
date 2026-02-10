$paths = @(
    "config/__init__.py",
    "src/__init__.py",
    "src/scraper/__init__.py",
    "src/processor/__init__.py",
    "src/media/__init__.py",
    "src/publisher/__init__.py",
    "src/utils/__init__.py",
    "tests/__init__.py"
)

foreach ($path in $paths) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType File -Path $path -Force | Out-Null
        Write-Host "Created $path"
    }
}
