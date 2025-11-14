# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for continuous integration and deployment. The pipeline includes automated testing, security scanning, code quality checks, and deployment to production.

## 📋 Workflows

### 1. Backend Tests (`backend-tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches (backend files only)
- Pull requests to `main` or `develop` branches (backend files only)

**Jobs:**
- **Test Matrix**: Tests on Python 3.11, 3.12, and 3.13
- **Services**: PostgreSQL 15 and Redis 7
- **Coverage**: Generates coverage reports and uploads to Codecov
- **Threshold**: Requires minimum 50% test coverage

**What it does:**
1. Sets up Python environment with dependencies
2. Creates test database and Redis instance
3. Runs Django migrations
4. Executes pytest with coverage reporting
5. Uploads coverage reports as artifacts
6. Runs linting (flake8, black, isort)
7. Performs security checks with bandit

### 2. Frontend Tests (`frontend-tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches (frontend files only)
- Pull requests to `main` or `develop` branches (frontend files only)

**Jobs:**
- **Build & Test**: Tests on Node.js 18.x and 20.x
- **Lighthouse**: Performance and accessibility audits
- **Security**: npm audit and vulnerability scanning

**What it does:**
1. Installs dependencies with `npm ci`
2. Runs ESLint for code quality
3. Checks TypeScript types
4. Builds Next.js application
5. Runs Lighthouse performance tests
6. Scans for security vulnerabilities

### 3. Security Scanning (`security-scan.yml`)

**Triggers:**
- Push to any branch
- Pull requests
- Daily scheduled runs at 2 AM UTC

**Jobs:**
- **Backend Security**: Bandit and Safety checks
- **Frontend Security**: npm audit and Snyk
- **CodeQL Analysis**: Advanced code security analysis
- **Dependency Review**: Checks for vulnerable dependencies
- **Secret Scanning**: TruffleHog for exposed secrets

**What it does:**
1. Scans backend code for security issues
2. Checks frontend dependencies for vulnerabilities
3. Runs GitHub's CodeQL security analysis
4. Reviews dependencies in pull requests
5. Scans for accidentally committed secrets

### 4. Deployment (`deploy.yml`)

**Triggers:**
- Push to `main` branch (auto-deploy)
- Manual workflow dispatch (choose staging/production)

**Jobs:**
- **Test**: Runs full test suite before deployment
- **Deploy Backend**: Deploys to Render
- **Deploy Frontend**: Deploys to Vercel
- **Health Check**: Validates deployed services
- **Notify**: Reports deployment status

**What it does:**
1. Runs tests to ensure code quality
2. Deploys backend to Render
3. Deploys frontend to Vercel
4. Performs health checks on deployed services
5. Runs smoke tests
6. Notifies team of deployment status

### 5. Pull Request Validation (`pr-validation.yml`)

**Triggers:**
- Pull request opened, synchronized, or reopened

**Jobs:**
- **PR Checks**: Validates PR title format
- **Code Review**: Automated review with Danger
- **Duplicate Check**: Detects code duplication
- **Conventional Commits**: Validates commit message format
- **Label Check**: Ensures PR has proper labels

**What it does:**
1. Validates PR follows semantic naming
2. Checks PR size (warns if too large)
3. Detects TODO/FIXME comments
4. Runs automated code review
5. Checks for code duplication
6. Validates commit messages follow conventions

## 🔐 Required Secrets

Set these in GitHub repository settings (Settings → Secrets and variables → Actions):

### Backend Deployment
- `RENDER_BACKEND_SERVICE_ID`: Render service ID for backend
- `RENDER_API_KEY`: Render API key
- `BACKEND_URL`: Production backend URL

### Frontend Deployment
- `VERCEL_TOKEN`: Vercel deployment token
- `VERCEL_ORG_ID`: Vercel organization ID
- `VERCEL_PROJECT_ID`: Vercel project ID
- `FRONTEND_URL`: Production frontend URL
- `API_URL`: Backend API URL for frontend

### Security & Monitoring
- `SNYK_TOKEN`: Snyk security scanning token (optional)
- `CODECOV_TOKEN`: Codecov upload token (optional)
- `LHCI_GITHUB_APP_TOKEN`: Lighthouse CI token (optional)

### Database & Services
- `DATABASE_URL`: Production database connection string
- `REDIS_URL`: Production Redis connection string
- `SECRET_KEY`: Django secret key
- `SENTRY_DSN`: Sentry error tracking DSN

## 🚀 Setup Instructions

### 1. Enable GitHub Actions

GitHub Actions is enabled by default for public repositories. For private repositories:
1. Go to Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"

### 2. Configure Secrets

Add all required secrets mentioned above:
```bash
# Example using GitHub CLI
gh secret set RENDER_API_KEY
gh secret set VERCEL_TOKEN
gh secret set DATABASE_URL
```

### 3. Set Up Branch Protection

Recommended branch protection rules for `main`:
1. Require pull request reviews (at least 1)
2. Require status checks to pass:
   - Backend Tests
   - Frontend Tests
   - Security Scanning
3. Require branches to be up to date
4. Include administrators in restrictions

### 4. Configure Render Deployment

1. Create a Render service for your backend
2. Set environment variables in Render dashboard
3. Get service ID from Render URL
4. Add service ID and API key to GitHub secrets

### 5. Configure Vercel Deployment

1. Install Vercel CLI: `npm i -g vercel`
2. Link project: `vercel link`
3. Get tokens: `vercel login`
4. Add tokens to GitHub secrets

## 📊 Monitoring & Reports

### Coverage Reports
- Coverage reports are uploaded as artifacts after each test run
- View in Actions → Workflow Run → Artifacts
- Minimum threshold: 50%

### Security Reports
- Bandit and npm audit reports saved as artifacts
- CodeQL alerts in Security tab
- Dependency review on pull requests

### Performance Monitoring
- Lighthouse scores on each PR
- Performance regression detection
- Accessibility and best practices audits

## 🔄 Workflow Best Practices

### Commit Messages
Follow conventional commits format:
```
feat(auth): add JWT token refresh
fix(api): resolve faculty endpoint error
docs(readme): update installation steps
test(models): add User model tests
```

### Pull Requests
- Keep PRs focused and small (<50 files, <500 lines)
- Add descriptive title following semantic format
- Add appropriate labels (bug, feature, etc.)
- Request reviews from team members
- Ensure all checks pass before merging

### Testing
- Write tests for new features
- Maintain >50% coverage
- Run tests locally before pushing:
  ```bash
  # Backend
  cd backend/django && pytest
  
  # Frontend
  cd frontend && npm test
  ```

## 🐛 Troubleshooting

### Tests Failing in CI but Pass Locally
- Check Python/Node versions match
- Ensure all dependencies are in requirements.txt/package.json
- Verify environment variables are set correctly
- Check for timezone or locale differences

### Deployment Fails
- Verify all secrets are set correctly
- Check service logs in Render/Vercel dashboard
- Ensure migrations run successfully
- Verify environment variables in production

### Security Alerts
- Review CodeQL alerts in Security tab
- Update vulnerable dependencies
- Fix high-severity issues immediately
- Address moderate issues in next release

## 📈 Continuous Improvement

### Current Metrics
- Test Coverage: 52.30%
- Build Time: ~3-5 minutes
- Deployment Time: ~2-3 minutes

### Goals
- Increase test coverage to 80%
- Reduce build time to <2 minutes
- Add end-to-end testing
- Implement canary deployments
- Add performance monitoring

## 🆘 Support

For CI/CD issues:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Check GitHub Actions status page
4. Contact DevOps team

---

**Last Updated:** November 14, 2025  
**Maintained By:** SIH28 Team
