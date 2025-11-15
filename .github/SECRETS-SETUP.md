# GitHub Secrets Setup Guide

## Quick Setup Checklist

- [ ] Render secrets configured
- [ ] Vercel secrets configured
- [ ] Database secrets configured
- [ ] Security tokens configured
- [ ] Test workflow execution

## Required Secrets

### 🔴 Critical (Required for Deployment)

#### Render Backend Deployment
```
RENDER_BACKEND_SERVICE_ID
RENDER_API_KEY
BACKEND_URL
```

**How to get:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your backend service
3. Service ID is in the URL: `https://dashboard.render.com/web/srv-XXXXXXXXXX`
4. API Key: Account Settings → API Keys → Create API Key
5. Backend URL: Your service URL (e.g., `https://your-app.onrender.com`)

#### Vercel Frontend Deployment
```
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
FRONTEND_URL
API_URL
```

**How to get:**
1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Link project: `cd frontend && vercel link`
4. Get IDs from `.vercel/project.json`
5. Token: [Vercel Account Settings → Tokens](https://vercel.com/account/tokens)
6. Frontend URL: Your Vercel deployment URL
7. API URL: Your backend URL for frontend API calls

#### Database & Services
```
DATABASE_URL
REDIS_URL
SECRET_KEY
```

**How to get:**
1. **DATABASE_URL**: From Neon dashboard → Connection Details
   - Format: `postgresql://user:password@host:5432/database?sslmode=require`
2. **REDIS_URL**: From Upstash dashboard → Redis → Details
   - Format: `redis://default:password@host:6379`
3. **SECRET_KEY**: Generate with:
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### 🟡 Optional (Enhanced Features)

#### Security Scanning
```
SNYK_TOKEN
```

**How to get:**
1. Sign up at [Snyk](https://snyk.io/)
2. Go to Account Settings → General → Auth Token
3. Copy token

#### Code Coverage
```
CODECOV_TOKEN
```

**How to get:**
1. Sign up at [Codecov](https://codecov.io/)
2. Add your repository
3. Copy upload token from repository settings

#### Performance Monitoring
```
LHCI_GITHUB_APP_TOKEN
SENTRY_DSN
```

**How to get:**
1. **Lighthouse CI**: [Install GitHub App](https://github.com/apps/lighthouse-ci)
2. **Sentry**: From [Sentry Project Settings](https://sentry.io/) → Client Keys (DSN)

## Setting Secrets in GitHub

### Method 1: GitHub Web UI

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter secret name and value
5. Click **Add secret**

### Method 2: GitHub CLI

```bash
# Install GitHub CLI if not installed
# https://cli.github.com/

# Login
gh auth login

# Set secrets
gh secret set RENDER_API_KEY
gh secret set VERCEL_TOKEN
gh secret set DATABASE_URL
gh secret set REDIS_URL
gh secret set SECRET_KEY
gh secret set SNYK_TOKEN
gh secret set CODECOV_TOKEN
```

### Method 3: Bulk Import

Create a `.env.secrets` file (⚠️ **DO NOT COMMIT**):
```bash
RENDER_BACKEND_SERVICE_ID=srv-xxxxx
RENDER_API_KEY=rnd_xxxxx
BACKEND_URL=https://your-app.onrender.com
VERCEL_TOKEN=xxxxxxxxxx
VERCEL_ORG_ID=team_xxxxx
VERCEL_PROJECT_ID=prj_xxxxx
FRONTEND_URL=https://your-app.vercel.app
API_URL=https://your-app.onrender.com
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://default:pass@host:6379
SECRET_KEY=django-insecure-xxxxx
SNYK_TOKEN=xxxxxxxxxx
CODECOV_TOKEN=xxxxxxxxxx
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

Then run:
```bash
# Set all secrets from file
while IFS='=' read -r key value; do
  [[ $key =~ ^#.*$ ]] && continue
  [[ -z $key ]] && continue
  gh secret set "$key" -b"$value"
done < .env.secrets

# Delete the file immediately
rm .env.secrets
```

## Verification

### Test Secrets Are Set

```bash
# List all secrets (values are hidden)
gh secret list
```

Expected output:
```
RENDER_BACKEND_SERVICE_ID  Updated 2025-01-14
RENDER_API_KEY             Updated 2025-01-14
BACKEND_URL                Updated 2025-01-14
VERCEL_TOKEN               Updated 2025-01-14
VERCEL_ORG_ID              Updated 2025-01-14
VERCEL_PROJECT_ID          Updated 2025-01-14
...
```

### Test Workflow Execution

1. Make a small change (e.g., update README)
2. Commit and push to a test branch
3. Create a pull request
4. Check GitHub Actions tab for workflow runs
5. Verify all jobs pass

## Security Best Practices

### ✅ DO

- Store all sensitive values as secrets
- Use different secrets for staging/production
- Rotate secrets regularly (every 90 days)
- Use least-privilege access
- Monitor secret usage in audit logs

### ❌ DON'T

- Commit secrets to repository
- Share secrets via chat/email
- Use production secrets in development
- Print secrets in logs
- Store secrets in code comments

## Environment-Specific Secrets

### Development
Use `.env` file locally (not committed):
```bash
# backend/django/.env
DEBUG=True
DATABASE_URL=postgresql://localhost/erp_dev
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev-secret-key-not-for-production
```

### Staging
Set in GitHub secrets with `STAGING_` prefix:
```
STAGING_DATABASE_URL
STAGING_REDIS_URL
STAGING_BACKEND_URL
```

### Production
Regular secret names (as listed above)

## Troubleshooting

### Secret Not Found Error
```
Error: Secret RENDER_API_KEY not found
```

**Solution:**
1. Verify secret name matches exactly (case-sensitive)
2. Check secret is set in correct repository
3. Ensure you have admin access to repository

### Invalid Secret Value
```
Error: Invalid credentials
```

**Solution:**
1. Regenerate secret from service provider
2. Update secret in GitHub
3. Verify no extra spaces or newlines

### Workflow Can't Access Secret
```
Error: Process completed with exit code 1
```

**Solution:**
1. Check workflow has correct `secrets:` reference
2. Verify secret name in workflow file
3. Ensure workflow runs from correct branch

## Updating Secrets

When secrets need to be rotated:

1. **Generate new secret** from service provider
2. **Update in GitHub**:
   ```bash
   gh secret set SECRET_NAME
   ```
3. **Test immediately** with workflow run
4. **Update in production** if workflow passes
5. **Revoke old secret** after verification

## Emergency Secret Rotation

If a secret is compromised:

1. **Immediately revoke** the compromised secret
2. **Generate new secret** from service provider
3. **Update GitHub secret** right away
4. **Deploy new secret** to production
5. **Review audit logs** to check for unauthorized access
6. **Update documentation** with incident details

---

**Need Help?**
- GitHub Actions Secrets: https://docs.github.com/actions/security-guides/encrypted-secrets
- Render Support: https://render.com/docs
- Vercel Support: https://vercel.com/docs
