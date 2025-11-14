# GitHub Secrets Configuration Checklist

## 🔐 Quick Setup Guide

**Repository:** https://github.com/harssh-ssarma/SIH28

**Navigate to:** Settings → Secrets and variables → Actions → New repository secret

---

## ✅ Secrets Configuration Status

### 🔴 CRITICAL - Required for Workflows to Run

#### Backend Deployment (Render)
- [ ] `RENDER_BACKEND_SERVICE_ID`
  - Where: Render Dashboard → Your Service → URL contains `srv-XXXXXXXXXX`
  - Example: `srv-abc123def456`
  
- [ ] `RENDER_API_KEY`
  - Where: Render Account Settings → API Keys → Create API Key
  - Example: `rnd_xxxxxxxxxxxxxxxxxxxxx`

- [ ] `BACKEND_URL`
  - Your Render service URL
  - Example: `https://sih28-backend.onrender.com`

#### Frontend Deployment (Vercel)
- [ ] `VERCEL_TOKEN`
  - Where: https://vercel.com/account/tokens → Create Token
  - Example: `xxxxxxxxxxxxxxxxxxxxxxxx`

- [ ] `VERCEL_ORG_ID`
  - Run: `cd frontend && vercel link` (creates .vercel/project.json)
  - Or from: Vercel Project Settings → General
  - Example: `team_xxxxxxxxxxxxxxxxxxxxx`

- [ ] `VERCEL_PROJECT_ID`
  - Same as above (in .vercel/project.json)
  - Example: `prj_xxxxxxxxxxxxxxxxxxxxx`

- [ ] `FRONTEND_URL`
  - Your Vercel deployment URL
  - Example: `https://sih28.vercel.app`

- [ ] `API_URL`
  - Backend URL for frontend API calls (same as BACKEND_URL)
  - Example: `https://sih28-backend.onrender.com`

#### Database & Services
- [ ] `DATABASE_URL`
  - Where: Neon Dashboard → Connection Details
  - Format: `postgresql://user:password@host:5432/database?sslmode=require`

- [ ] `REDIS_URL`
  - Where: Upstash Dashboard → Redis → Details
  - Format: `redis://default:password@host:6379`

- [ ] `SECRET_KEY`
  - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  - Example: `django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### 🟡 RECOMMENDED - Enhanced Features

#### Security Scanning
- [ ] `SNYK_TOKEN`
  - Where: https://snyk.io/ → Account Settings → Auth Token
  - **Purpose**: Advanced security vulnerability scanning
  - **Impact**: Better security reports

- [ ] `CODECOV_TOKEN`
  - Where: https://codecov.io/ → Repository Settings → Upload Token
  - **Purpose**: Code coverage tracking and visualization
  - **Impact**: Coverage trend analysis

#### Performance Monitoring
- [ ] `LHCI_GITHUB_APP_TOKEN`
  - Where: Install https://github.com/apps/lighthouse-ci
  - **Purpose**: Lighthouse performance tracking
  - **Impact**: Performance regression detection

- [ ] `SENTRY_DSN`
  - Where: https://sentry.io/ → Project Settings → Client Keys (DSN)
  - **Purpose**: Error tracking and performance monitoring
  - **Impact**: Real-time error alerts

---

## 📋 Quick Command Reference

### Generate Django Secret Key
```powershell
cd d:\GitHub\SIH28\backend\django
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Get Vercel Project IDs
```powershell
cd d:\GitHub\SIH28\frontend
vercel link
# IDs will be in .vercel/project.json
Get-Content .vercel\project.json
```

### Test Secret Configuration (GitHub CLI)
```powershell
# Install GitHub CLI: https://cli.github.com/
gh auth login
gh secret list
```

---

## 🚀 Set Secrets via GitHub CLI (Faster)

```powershell
# Set critical secrets
gh secret set RENDER_BACKEND_SERVICE_ID
gh secret set RENDER_API_KEY
gh secret set BACKEND_URL
gh secret set VERCEL_TOKEN
gh secret set VERCEL_ORG_ID
gh secret set VERCEL_PROJECT_ID
gh secret set FRONTEND_URL
gh secret set API_URL
gh secret set DATABASE_URL
gh secret set REDIS_URL
gh secret set SECRET_KEY

# Set optional secrets
gh secret set SNYK_TOKEN
gh secret set CODECOV_TOKEN
gh secret set SENTRY_DSN
```

---

## 🔍 Verify Configuration

### 1. Check Secrets Are Set
```powershell
gh secret list
```

Expected output shows all secrets (values hidden):
```
BACKEND_URL                Updated 2025-11-14
DATABASE_URL               Updated 2025-11-14
REDIS_URL                  Updated 2025-11-14
RENDER_API_KEY             Updated 2025-11-14
RENDER_BACKEND_SERVICE_ID  Updated 2025-11-14
SECRET_KEY                 Updated 2025-11-14
VERCEL_ORG_ID              Updated 2025-11-14
VERCEL_PROJECT_ID          Updated 2025-11-14
VERCEL_TOKEN               Updated 2025-11-14
...
```

### 2. Check Workflow Status
Visit: https://github.com/harssh-ssarma/SIH28/actions

Look for:
- ✅ Backend Tests (should be running or completed)
- ✅ Frontend Tests (should be running or completed)
- ✅ Security Scan (should be running or completed)
- ⏳ Deploy (will fail without secrets, pass after configuration)

### 3. Review Workflow Logs
Click on any workflow run to see detailed logs and identify missing secrets.

---

## ❌ Common Issues & Solutions

### Issue: "Secret not found"
**Solution:** Secret name must match exactly (case-sensitive)
```powershell
# Correct
gh secret set DATABASE_URL

# Wrong
gh secret set database_url
```

### Issue: "Invalid credentials" in workflow
**Solution:** Verify secret values are correct
1. Delete the secret: `gh secret delete SECRET_NAME`
2. Recreate with correct value: `gh secret set SECRET_NAME`

### Issue: Workflows not triggering
**Solution:** Check workflow triggers in `.github/workflows/*.yml`
- Backend: Triggers on `backend/**` changes
- Frontend: Triggers on `frontend/**` changes
- Security: Triggers on all pushes + daily schedule

### Issue: Deploy workflow fails
**Solution:** Configure all deployment secrets first
- Deployment will fail until ALL secrets are set
- Start with CRITICAL secrets only
- Test with a small commit after configuration

---

## 📊 Current Status

**Workflows Pushed:** ✅ 5 workflows active
**Secrets Configured:** ⏳ Pending
**Test Commit:** ✅ Pushed (commit 5bdab95)
**Workflows Triggered:** Check https://github.com/harssh-ssarma/SIH28/actions

---

## 🎯 Priority Actions

1. **NOW:** Configure CRITICAL secrets (9 secrets) - 10-15 minutes
2. **NEXT:** Verify workflows pass on GitHub Actions
3. **THEN:** Configure RECOMMENDED secrets for enhanced features
4. **FINALLY:** Update todo list to mark CI/CD setup as complete

---

## 📞 Need Help?

- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **GitHub Actions:** https://docs.github.com/actions
- **Secrets Guide:** See `.github/SECRETS-SETUP.md` for detailed instructions

---

**Last Updated:** November 14, 2025
**Ready for Configuration:** ✅ All workflows deployed and active
