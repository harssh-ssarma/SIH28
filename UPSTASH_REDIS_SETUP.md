# Upstash Redis Setup Instructions

## Step 1: Get Your Upstash Redis URL

Go to your Upstash Console and copy the **Redis URL** (should look like):
```
rediss://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379
```

## Step 2: Set Environment Variable

### Option A: For Current Terminal Session (Temporary)
```powershell
$env:REDIS_URL="rediss://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379"
```

### Option B: Create .env file (Permanent)
Create file: `D:\GitHub\SIH28\backend\django\.env`
```env
REDIS_URL=rediss://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379
```

Then install python-dotenv:
```powershell
pip install python-dotenv
```

And update `erp/settings.py` at the top:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option C: Windows Environment Variable (System-wide)
```powershell
# Run as Administrator
[System.Environment]::SetEnvironmentVariable('REDIS_URL', 'rediss://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379', 'User')
```
Then restart your terminal.

## Step 3: Test Connection
```powershell
cd D:\GitHub\SIH28\backend\django
python test_redis.py
```

Should show:
```
✓ Redis Working: True
✓ Cache Persists: True
Total Keys: XX
```

## Step 4: Restart Django
```powershell
python manage.py runserver
```

## Troubleshooting

### If you see "Connection closed by server"
- Check if REDIS_URL is set: `echo $env:REDIS_URL`
- Verify URL format starts with `rediss://` (double 's' for TLS)
- Check password is correct
- Ensure Upstash Redis instance is active

### If you see "Authentication failed"
- Password might be wrong
- Try copying the URL directly from Upstash console

### Quick Test Without Django
```powershell
pip install redis

python -c "import redis; r = redis.from_url('YOUR_REDIS_URL'); r.ping(); print('Connected!')"
```

## After Setup

Your cache will work automatically:
- First request: 2-3s (Cache MISS)
- Subsequent: 50ms (Cache HIT) ⚡
- LCP will drop to < 2.5s
