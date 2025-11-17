# Quick Setup for Upstash Redis
# Replace YOUR_UPSTASH_URL with your actual Upstash Redis URL from the console

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Upstash Redis Quick Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Prompt for Redis URL
Write-Host "Please enter your Upstash Redis URL:" -ForegroundColor Yellow
Write-Host "(Format: rediss://default:PASSWORD@endpoint.upstash.io:6379)" -ForegroundColor Gray
$redisUrl = Read-Host "Redis URL"

if ([string]::IsNullOrWhiteSpace($redisUrl)) {
    Write-Host "Error: Redis URL cannot be empty!" -ForegroundColor Red
    exit 1
}

# Validate format
if (-not $redisUrl.StartsWith("redis://") -and -not $redisUrl.StartsWith("rediss://")) {
    Write-Host "Warning: URL should start with 'redis://' or 'rediss://'" -ForegroundColor Yellow
}

# Set environment variable for current session
$env:REDIS_URL = $redisUrl
Write-Host ""
Write-Host "✓ REDIS_URL set for current session" -ForegroundColor Green

# Create or update .env file
$envPath = "D:\GitHub\SIH28\backend\.env"
$envContent = ""

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    if ($envContent -match "REDIS_URL=") {
        $envContent = $envContent -replace "REDIS_URL=.*", "REDIS_URL=$redisUrl"
        Write-Host "✓ Updated REDIS_URL in .env file" -ForegroundColor Green
    } else {
        $envContent += "`nREDIS_URL=$redisUrl"
        Write-Host "✓ Added REDIS_URL to .env file" -ForegroundColor Green
    }
} else {
    $envContent = "REDIS_URL=$redisUrl"
    Write-Host "✓ Created .env file with REDIS_URL" -ForegroundColor Green
}

Set-Content -Path $envPath -Value $envContent

Write-Host ""
Write-Host "Testing Redis connection..." -ForegroundColor Cyan

# Test connection
cd D:\GitHub\SIH28\backend\django
$testOutput = python test_redis.py 2>&1

if ($testOutput -match "Redis Working: True") {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "  ✓ Redis Connected Successfully!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Restart Django: python manage.py runserver" -ForegroundColor White
    Write-Host "2. Visit Faculty/Students pages" -ForegroundColor White
    Write-Host "3. First load: ~2s, Second load: ~50ms ⚡" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "  ✗ Redis Connection Failed" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. Redis URL is correct" -ForegroundColor White
    Write-Host "2. Upstash instance is active" -ForegroundColor White
    Write-Host "3. Password is correct" -ForegroundColor White
    Write-Host ""
    Write-Host "Full output:" -ForegroundColor Gray
    Write-Host $testOutput
}
