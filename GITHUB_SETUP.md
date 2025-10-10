# GitHub Setup and Deployment Guide
## Connecting Your Wealth Coach AI to GitHub

---

## ✅ **Current Status**

- [x] Git repository initialized
- [x] Initial commit created (139 files, 23,573 lines)
- [x] `.gitignore` configured
- [x] GitHub Actions workflows created
- [ ] Connected to GitHub remote
- [ ] Pushed to GitHub
- [ ] GitHub Actions enabled

---

## 🚀 **Step-by-Step GitHub Setup**

### **Step 1: Create GitHub Repository**

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `wealth-coach-ai` (or your preferred name)
   - **Description**: AI-powered Financial Advisor with RAG
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have them)
3. Click "Create repository"

### **Step 2: Connect Local Repository to GitHub**

After creating the repository, run these commands:

```bash
# Add GitHub as remote origin
git remote add origin https://github.com/Sour4vH4ld3r/wealth-coach-ai.git

# Verify remote was added
git remote -v

# Push to GitHub
git push -u origin main
```

**OR if you prefer SSH:**

```bash
# Add GitHub as remote origin (SSH)
git remote add origin git@github.com:Sour4vH4ld3r/wealth-coach-ai.git

# Push to GitHub
git push -u origin main
```

### **Step 3: Verify Upload**

1. Go to your repository: https://github.com/Sour4vH4ld3r/wealth-coach-ai
2. You should see all your files
3. Check the Actions tab - workflows should be detected

---

## 🔧 **GitHub Actions Setup**

### **Workflows Created**

1. **`docker-build-push.yml`** - Build and push Docker images to GitHub Container Registry
2. **`ci.yml`** - Run tests and quality checks on every push/PR
3. **`docker-hub.yml`** - (Optional) Push to Docker Hub instead

### **Enable GitHub Actions**

Actions should be enabled automatically. To verify:

1. Go to repository Settings → Actions → General
2. Ensure "Allow all actions and reusable workflows" is selected
3. Click "Save"

### **Required Secrets for Full Automation**

Go to Settings → Secrets and variables → Actions → New repository secret

#### **For Docker Hub Deployment (Optional)**
- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token

#### **For Production Deployment**
- `DEPLOY_HOST` - Production server IP/hostname
- `DEPLOY_USER` - SSH username
- `DEPLOY_SSH_KEY` - SSH private key for deployment

### **Generate Docker Hub Token**

1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name: "GitHub Actions"
4. Copy the token and add to GitHub secrets

### **Generate SSH Key for Deployment**

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub user@your-server.com

# Copy private key content
cat ~/.ssh/github_actions_deploy
# Paste this into DEPLOY_SSH_KEY secret
```

---

## 📦 **What Happens When You Push**

### **On Every Push to `main` or `develop`:**

1. **CI Workflow Runs:**
   - ✅ Lints Python code (flake8, black)
   - ✅ Runs backend tests
   - ✅ Lints frontend code
   - ✅ Builds frontend
   - ✅ Security scans (Bandit, Safety, TruffleHog)
   - ✅ Dependency vulnerability checks

2. **Docker Build Workflow Runs:**
   - ✅ Builds backend Docker image
   - ✅ Builds frontend Docker image
   - ✅ Pushes to GitHub Container Registry (ghcr.io)
   - ✅ Scans images for vulnerabilities (Trivy)
   - ✅ (Optional) Deploys to production server

### **On Pull Requests:**
- ✅ Runs all CI checks
- ✅ Builds Docker images (doesn't push)
- ✅ Shows status in PR

### **On Version Tags (`v*`):**
- ✅ Builds and tags with version number
- ✅ Creates semantic versioning tags (e.g., `v1.0.0`, `v1.0`, `v1`)

---

## 🐳 **Using Docker Images from GitHub**

### **Pull Images from GitHub Container Registry**

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull backend image
docker pull ghcr.io/sour4vh4ld3r/wealth-coach-ai/backend:latest

# Pull frontend image
docker pull ghcr.io/sour4vh4ld3r/wealth-coach-ai/frontend:latest

# Run with docker-compose using GitHub images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### **Make Images Public (Recommended)**

1. Go to https://github.com/users/Sour4vH4ld3r/packages
2. Click on your package (backend or frontend)
3. Click "Package settings"
4. Scroll to "Danger Zone"
5. Click "Change visibility" → Make public

Now anyone can pull your images without authentication!

---

## 🔄 **Continuous Deployment Workflow**

### **Automatic Deployment Flow**

```
Code Push → GitHub Actions → Docker Build → Push to Registry → Deploy to Server → Health Check
```

### **Manual Deployment**

Trigger deployment manually:

1. Go to Actions tab
2. Select "Docker Build and Push" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

---

## 📝 **Best Practices**

### **Branch Strategy**

```
main (production)
  ↑
develop (staging)
  ↑
feature/feature-name (development)
```

### **Commit Messages**

Follow conventional commits:

```bash
feat: Add user authentication
fix: Resolve vector search timeout
docs: Update deployment guide
chore: Update dependencies
refactor: Improve caching logic
test: Add unit tests for RAG retriever
```

### **Version Tagging**

```bash
# Create a new version
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# This triggers Docker build with version tags
```

---

## 🔒 **Security Best Practices**

### **Never Commit Secrets**

✅ Already configured in `.gitignore`:
- `.env` files
- API keys
- SSL certificates
- SSH keys
- Credentials

### **Use GitHub Secrets**

- All sensitive data in GitHub Secrets
- Reference in workflows as: `${{ secrets.SECRET_NAME }}`
- Never echo secrets in workflow logs

### **Review Dependency Security**

GitHub Dependabot will:
- Scan for vulnerabilities
- Create PRs to update dependencies
- Alert you to security issues

Enable Dependabot:
1. Settings → Code security and analysis
2. Enable "Dependabot alerts"
3. Enable "Dependabot security updates"

---

## 📊 **Monitoring GitHub Actions**

### **View Workflow Runs**

1. Go to Actions tab
2. See all workflow runs
3. Click on a run to see details
4. View logs for each job/step

### **Get Notifications**

Settings → Notifications:
- Enable "Actions" notifications
- Get notified on failures
- Configure email or Slack integration

### **Add Status Badges to README**

Add to your README.md:

```markdown
![CI](https://github.com/Sour4vH4ld3r/wealth-coach-ai/workflows/CI/badge.svg)
![Docker Build](https://github.com/Sour4vH4ld3r/wealth-coach-ai/workflows/Docker%20Build%20and%20Push/badge.svg)
```

---

## 🛠️ **Troubleshooting**

### **Issue: Workflow Fails on First Run**

**Solution:** Add secrets before pushing:
```bash
# Check what secrets are needed
grep -r "secrets\." .github/workflows/
```

### **Issue: Docker Build Out of Space**

**Solution:** GitHub Actions has 14GB limit. Optimize:
- Use multi-stage builds (already done)
- Remove unnecessary dependencies
- Use `.dockerignore`

### **Issue: Can't Push to GitHub**

**Solution:** Check authentication:
```bash
# For HTTPS
git remote set-url origin https://github.com/Sour4vH4ld3r/wealth-coach-ai.git

# For SSH
git remote set-url origin git@github.com:Sour4vH4ld3r/wealth-coach-ai.git
```

---

## 📚 **Additional Resources**

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Docker Hub**: https://hub.docker.com
- **GitHub Packages**: https://docs.github.com/en/packages
- **Dependabot**: https://docs.github.com/en/code-security/dependabot

---

## ✅ **Quick Checklist**

Before pushing to GitHub:

- [x] Git repository initialized
- [x] Initial commit made
- [x] `.gitignore` configured
- [x] GitHub Actions workflows created
- [ ] GitHub repository created
- [ ] Remote origin added
- [ ] Pushed to GitHub
- [ ] GitHub Actions secrets configured (if needed)
- [ ] Dependabot enabled
- [ ] Package visibility set to public

---

## 🎯 **Next Steps**

1. **Create GitHub repository** (Step 1 above)
2. **Connect local repo** (Step 2 above)
3. **Push to GitHub**: `git push -u origin main`
4. **Check Actions tab** to see workflows run
5. **Add secrets** for Docker Hub/deployment (if needed)
6. **Enable Dependabot** for security
7. **Add README badges** for status visibility

---

**Ready to push!** 🚀

```bash
git push -u origin main
```
