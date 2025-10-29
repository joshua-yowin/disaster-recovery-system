SETUP INSTRUCTIONS
Step 1: Install Python Dependencies in VS Code

bash
# Open VS Code terminal (Ctrl+`)
cd disaster-recovery-system

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import flask; print('✅ Flask installed')"
Step 2: Test Locally in VS Code

bash
# Test backup system
python3 app/backup.py

# Start dashboard
python3 dashboard/monitoring_dashboard.py

# Open browser: http://localhost:5000
📤 PART 4: PUSH TO GITHUB
Step 1: Create GitHub Repository

Go to https://github.com/new

Repository name: disaster-recovery-system

Description: Automated Disaster Recovery Backup System with CI/CD

Public/Private: Your choice

Click "Create repository"

Step 2: Push Code from VS Code

bash
# In VS Code terminal
git add .
git commit -m "Initial commit: Complete disaster recovery system"

# Add remote (replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/disaster-recovery-system.git

# Push to GitHub
git push -u origin main

# ✅ Code now on GitHub!
🔧 PART 5: JENKINS SETUP (Simplified)
Step 1: Install Jenkins on Your Machine

Option A: Windows

powershell
# Download Jenkins Windows installer
# https://www.jenkins.io/download/

# Install and start Jenkins
# Access: http://localhost:8080
Option B: macOS

bash
# Install with Homebrew
brew install jenkins-lts

# Start Jenkins
brew services start jenkins-lts

# Access: http://localhost:8080
Option C: Linux

bash
# Install Java
sudo apt update
sudo apt install openjdk-11-jdk -y

# Install Jenkins
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt update
sudo apt install jenkins -y

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Access: http://localhost:8080
Step 2: Configure Jenkins

bash
# Get initial password
# Windows: C:\Program Files\Jenkins\secrets\initialAdminPassword
# macOS: /Users/Shared/Jenkins/Home/secrets/initialAdminPassword
# Linux: /var/lib/jenkins/secrets/initialAdminPassword

cat /var/lib/jenkins/secrets/initialAdminPassword
Open http://localhost:8080

Paste password

Click "Install suggested plugins"

Create admin user

Click "Start using Jenkins"

Step 3: Create Pipeline in Jenkins

Click "New Item"

Name: disaster-recovery-pipeline

Type: Pipeline

Click OK

Configure Pipeline:

General → Check "GitHub project" → Paste your GitHub repo URL

Build Triggers → Check "Poll SCM" → Schedule: H/5 * * * *

Pipeline → Definition: Pipeline script from SCM

SCM: Git

Repository URL: https://github.com/YOUR_USERNAME/disaster-recovery-system.git

Credentials: Add GitHub token (if private repo)

Branch: */main

Script Path: jenkins/Jenkinsfile

Step 4: Test Jenkins Pipeline

bash
# In VS Code, make a change
echo "# Test Jenkins" >> README.md

# Commit and push
git add README.md
git commit -m "Test Jenkins pipeline"
git push origin main

# Go to Jenkins: http://localhost:8080
# Click on disaster-recovery-pipeline
# Should see build starting automatically!
☁️ PART 6: AZURE DEPLOYMENT
Step 1: Azure Student Setup

bash
# Login to Azure
az login

# Verify student subscription
az account list --output table

# Set subscription
az account set --subscription "Azure for Students"
Step 2: Create Azure Resources

bash
# Create resource group
az group create --name disaster-recovery-rg --location eastus

# Create storage account (for backups)
az storage account create \
  --name dr backup$(date +%s) \
  --resource-group disaster-recovery-rg \
  --location eastus \
  --sku Standard_LRS

# Get connection string
az storage account show-connection-string \
  --name drbackup* \
  --resource-group disaster-recovery-rg \
  --output tsv
Step 3: Deploy Web App to Azure

bash
# Create App Service Plan (Free tier for students)
az appservice plan create \
  --name disaster-recovery-plan \
  --resource-group disaster-recovery-rg \
  --sku F1 \
  --is-linux

# Create Web App
az webapp create \
  --name disaster-recovery-dashboard \
  --resource-group disaster-recovery-rg \
  --plan disaster-recovery-plan \
  --runtime "PYTHON:3.9"

# Deploy code
cd disaster-recovery-system
zip -r deploy.zip app dashboard requirements.txt

az webapp deployment source config-zip \
  --resource-group disaster-recovery-rg \
  --name disaster-recovery-dashboard \
  --src deploy.zip

# Get URL
az webapp show \
  --name disaster-recovery-dashboard \
  --resource-group disaster-recovery-rg \
  --query defaultHostName --output tsv

# Access your app at: https://disaster-recovery-dashboard.azurewebsites.net
📊 COMPLETE WORKFLOW
text
┌─────────────────────────────────────────────────────────┐
│              YOUR DEVELOPMENT WORKFLOW                   │
└─────────────────────────────────────────────────────────┘

1. 💻 VS Code - Write Code
   ↓
2. 🧪 Test Locally
   python3 app/backup.py
   python3 dashboard/monitoring_dashboard.py
   ↓
3. 📤 Push to GitHub
   git add .
   git commit -m "Update"
   git push origin main
   ↓
4. 🔧 Jenkins Auto-Triggers
   - Checks out code
   - Runs tests
   - Creates backup
   - Archives artifacts
   ↓
5. ☁️ Azure Deployment (manual or automated)
   az webapp deploy...
   ↓
6. 📊 Monitor Dashboard
   https://your-app.azurewebsites.net
✅ VERIFICATION CHECKLIST
bash
# ✅ Test local backup
python3 app/backup.py

# ✅ Test dashboard
python3 dashboard/monitoring_dashboard.py
# Open: http://localhost:5000

# ✅ Verify GitHub push
git status
git push origin main

# ✅ Check Jenkins build
# http://localhost:8080

# ✅ Verify Azure deployment
az webapp show --name disaster-recovery-dashboard --resource-group disaster-recovery-rg

# ✅ Access live dashboard
# https://disaster-recovery-dashboard.azurewebsites.net
🎯 QUICK START SCRIPT
Save this as quickstart.sh:

bash
#!/bin/bash

echo "🚀 Disaster Recovery System - Quick Start"
echo "=========================================="

# 1. Setup
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# 2. Test backup
echo "💾 Testing backup system..."
python3 app/backup.py

# 3. Start dashboard
echo "📊 Starting dashboard..."
python3 dashboard/monitoring_dashboard.py &

echo ""
echo "✅ System ready!"
echo "📊 Dashboard: http://localhost:5000"
echo "🔧 Jenkins: http://localhost:8080"
Run it:

bash
chmod +x quickstart.sh
./quickstart.sh
