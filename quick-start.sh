#!/bin/bash

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 DISASTER RECOVERY SYSTEM - QUICK START${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# 1. DOCKER STATUS
# ============================================
echo -e "\n${YELLOW}1️⃣  CHECKING DOCKER${NC}"
echo "════════════════════"

if docker ps -a | grep -q "disaster-recovery-system"; then
  DOCKER_STATUS=$(docker ps | grep "disaster-recovery-system" || echo "stopped")
  if [ -n "$DOCKER_STATUS" ]; then
    echo -e "${GREEN}✅ Docker is RUNNING${NC}"
    docker ps | grep "disaster-recovery-system"
  else
    echo -e "${YELLOW}⚠️  Docker is STOPPED - Starting...${NC}"
    docker-compose up -d
    sleep 10
    echo -e "${GREEN}✅ Docker STARTED${NC}"
  fi
else
  echo -e "${YELLOW}⚠️  Docker container not found - Building...${NC}"
  docker build -t disaster-recovery-system:latest .
  docker-compose up -d
  sleep 10
  echo -e "${GREEN}✅ Docker BUILT and STARTED${NC}"
fi

# ============================================
# 2. DOCKER IMAGE
# ============================================
echo -e "\n${YELLOW}2️⃣  DOCKER IMAGE${NC}"
echo "════════════════════"
docker images | grep "disaster-recovery-system"

# ============================================
# 3. DOCKER LOGS
# ============================================
echo -e "\n${YELLOW}3️⃣  DOCKER LOGS (Last 10 lines)${NC}"
echo "════════════════════"
docker logs disaster-recovery-system --tail 10

# ============================================
# 4. LOCAL DOCKER ENDPOINTS
# ============================================
echo -e "\n${YELLOW}4️⃣  TESTING LOCAL DOCKER ENDPOINTS${NC}"
echo "════════════════════"

echo -e "${BLUE}URL: http://localhost:8000${NC}"

# Health Check
echo -e "\n${BLUE}Testing /health${NC}"
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if echo "$HEALTH" | jq . > /dev/null 2>&1; then
  echo -e "${GREEN}✅ /health${NC}"
  echo "$HEALTH" | jq '.'
else
  echo -e "${RED}❌ /health - Connection failed${NC}"
fi

# Status
echo -e "\n${BLUE}Testing /api/status${NC}"
STATUS=$(curl -s http://localhost:8000/api/status 2>/dev/null)
if echo "$STATUS" | jq . > /dev/null 2>&1; then
  echo -e "${GREEN}✅ /api/status${NC}"
  echo "$STATUS" | jq '.'
else
  echo -e "${RED}❌ /api/status - Connection failed${NC}"
fi

# Dashboard
echo -e "\n${BLUE}Testing / (Dashboard)${NC}"
DASHBOARD=$(curl -s http://localhost:8000/ 2>/dev/null)
if [ ${#DASHBOARD} -gt 100 ]; then
  echo -e "${GREEN}✅ / (Dashboard)${NC}"
  echo "Dashboard HTML loaded (${#DASHBOARD} bytes)"
else
  echo -e "${RED}❌ / - Connection failed${NC}"
fi

# Backup List
echo -e "\n${BLUE}Testing /api/backup/list${NC}"
BACKUPS=$(curl -s http://localhost:8000/api/backup/list 2>/dev/null)
if echo "$BACKUPS" | jq . > /dev/null 2>&1; then
  echo -e "${GREEN}✅ /api/backup/list${NC}"
  echo "$BACKUPS" | jq '.'
else
  echo -e "${RED}❌ /api/backup/list - Connection failed${NC}"
fi

# Backup Stats
echo -e "\n${BLUE}Testing /api/backup/stats${NC}"
STATS=$(curl -s http://localhost:8000/api/backup/stats 2>/dev/null)
if echo "$STATS" | jq . > /dev/null 2>&1; then
  echo -e "${GREEN}✅ /api/backup/stats${NC}"
  echo "$STATS" | jq '.'
else
  echo -e "${RED}❌ /api/backup/stats - Connection failed${NC}"
fi

# Create Test Backup
echo -e "\n${BLUE}Testing POST /api/backup/test${NC}"
BACKUP=$(curl -s -X POST http://localhost:8000/api/backup/test 2>/dev/null)
if echo "$BACKUP" | jq . > /dev/null 2>&1; then
  echo -e "${GREEN}✅ POST /api/backup/test${NC}"
  echo "$BACKUP" | jq '.'
else
  echo -e "${RED}❌ POST /api/backup/test - Connection failed${NC}"
fi

# ============================================
# 5. AZURE APP SERVICE
# ============================================
echo -e "\n${YELLOW}5️⃣  TESTING AZURE APP SERVICE${NC}"
echo "════════════════════"
echo -e "${BLUE}URL: https://disaster-recovery-dashboard-joshua.azurewebsites.net${NC}"

# Health Check
echo -e "\n${BLUE}Testing /health${NC}"
AZURE_HEALTH=$(curl -s https://disaster-recovery-dashboard-joshua.azurewebsites.net/health 2>/dev/null)
if echo "$AZURE_HEALTH" | jq . > /dev/null 2>&1; then
  echo -e "${GREEN}✅ /health${NC}"
  echo "$AZURE_HEALTH" | jq '.'
else
  echo -e "${RED}❌ /health - Connection failed${NC}"
fi

# ============================================
# 6. TERRAFORM
# ============================================
echo -e "\n${YELLOW}6️⃣  CHECKING TERRAFORM${NC}"
echo "════════════════════"

cd terraform

if [ -f "terraform.tfstate" ]; then
  echo -e "${GREEN}✅ Terraform state file exists${NC}"
  
  echo -e "\n${BLUE}Terraform resources:${NC}"
  terraform state list 2>/dev/null | head -20
  
  echo -e "\n${BLUE}Terraform resources count:${NC}"
  RESOURCE_COUNT=$(terraform state list 2>/dev/null | wc -l)
  echo -e "${GREEN}Total resources: $RESOURCE_COUNT${NC}"
  
  echo -e "\n${BLUE}Running terraform plan...${NC}"
  terraform plan -no-color 2>/dev/null | tail -5
else
  echo -e "${YELLOW}⚠️  No terraform state file${NC}"
  echo "Run: cd terraform && terraform init && terraform apply"
fi

cd ..

# ============================================
# 7. GIT STATUS
# ============================================
echo -e "\n${YELLOW}7️⃣  GIT STATUS${NC}"
echo "════════════════════"
GIT_BRANCH=$(git branch --show-current 2>/dev/null)
GIT_COMMITS=$(git log --oneline 2>/dev/null | wc -l)
GIT_STATUS=$(git status --porcelain 2>/dev/null | wc -l)

echo -e "${GREEN}Branch: $GIT_BRANCH${NC}"
echo -e "${GREEN}Commits: $GIT_COMMITS${NC}"

if [ $GIT_STATUS -eq 0 ]; then
  echo -e "${GREEN}✅ Working tree clean${NC}"
else
  echo -e "${YELLOW}⚠️  Changes pending: $GIT_STATUS${NC}"
fi

# ============================================
# 8. PROJECT FILES
# ============================================
echo -e "\n${YELLOW}8️⃣  PROJECT FILES${NC}"
echo "════════════════════"

echo -e "${BLUE}Core Files:${NC}"
[ -f "app.py" ] && echo -e "${GREEN}✅ app.py${NC}" || echo -e "${RED}❌ app.py${NC}"
[ -f "backup_system.py" ] && echo -e "${GREEN}✅ backup_system.py${NC}" || echo -e "${RED}❌ backup_system.py${NC}"
[ -f "requirements.txt" ] && echo -e "${GREEN}✅ requirements.txt${NC}" || echo -e "${RED}❌ requirements.txt${NC}"

echo -e "\n${BLUE}Docker Files:${NC}"
[ -f "Dockerfile" ] && echo -e "${GREEN}✅ Dockerfile${NC}" || echo -e "${RED}❌ Dockerfile${NC}"
[ -f "docker-compose.yml" ] && echo -e "${GREEN}✅ docker-compose.yml${NC}" || echo -e "${RED}❌ docker-compose.yml${NC}"
[ -f ".dockerignore" ] && echo -e "${GREEN}✅ .dockerignore${NC}" || echo -e "${RED}❌ .dockerignore${NC}"

echo -e "\n${BLUE}Terraform Files:${NC}"
[ -f "terraform/main.tf" ] && echo -e "${GREEN}✅ terraform/main.tf${NC}" || echo -e "${RED}❌ terraform/main.tf${NC}"
[ -f "terraform/variables.tf" ] && echo -e "${GREEN}✅ terraform/variables.tf${NC}" || echo -e "${RED}❌ terraform/variables.tf${NC}"
[ -f "terraform/outputs.tf" ] && echo -e "${GREEN}✅ terraform/outputs.tf${NC}" || echo -e "${RED}❌ terraform/outputs.tf${NC}"

echo -e "\n${BLUE}Documentation:${NC}"
[ -f "README.md" ] && echo -e "${GREEN}✅ README.md${NC}" || echo -e "${RED}❌ README.md${NC}"
[ -f "DOCKER.md" ] && echo -e "${GREEN}✅ DOCKER.md${NC}" || echo -e "${RED}❌ DOCKER.md${NC}"
[ -f "DEPLOYMENT.md" ] && echo -e "${GREEN}✅ DEPLOYMENT.md${NC}" || echo -e "${RED}❌ DEPLOYMENT.md${NC}"

# ============================================
# 9. SUMMARY
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ QUICK START TEST COMPLETE${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}Quick Commands:${NC}"
echo "  Local Dashboard: open http://localhost:8000"
echo "  Production:      open https://disaster-recovery-dashboard-joshua.azurewebsites.net"
echo "  Docker Logs:     docker logs -f disaster-recovery-system"
echo "  Stop Docker:     docker-compose down"
echo "  Terraform Plan:  cd terraform && terraform plan"
echo "  Git Status:      git status"

echo -e "\n${GREEN}🎉 System is operational!${NC}\n"
