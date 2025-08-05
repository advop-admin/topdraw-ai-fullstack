#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Topsdraw Blueprint Generator Installation...${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to show progress
show_progress() {
    echo -e "${YELLOW}➡️ $1...${NC}"
}

# Check and install system dependencies
show_progress "Checking system dependencies"
apt-get update
apt-get install -y \
    curl \
    git \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker if not exists
if ! command_exists docker; then
    show_progress "Installing Docker"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
fi

# Install Docker Compose if not exists
if ! command_exists docker-compose; then
    show_progress "Installing Docker Compose"
    curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create installation directory
INSTALL_DIR="/opt/topsdraw"
show_progress "Creating installation directory at ${INSTALL_DIR}"
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Clone repository
show_progress "Cloning repository"
git clone https://github.com/advop-admin/topdraw-ai-fullstack.git .

# Setup environment file
show_progress "Setting up environment configuration"
cat > .env << EOL
# Generate random passwords
POSTGRES_USER=topsdraw
POSTGRES_PASSWORD=$(openssl rand -base64 12)
POSTGRES_DB=topsdraw

# You'll need to set this manually
GEMINI_API_KEY=your_key_here
EOL

# Setup user permissions
show_progress "Setting up permissions"
usermod -aG docker $SUDO_USER
chown -R $SUDO_USER:$SUDO_USER $INSTALL_DIR

# Start services
show_progress "Starting services"
docker compose up -d

# Print success message
echo -e "\n${GREEN}✅ Installation completed successfully!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Set your Gemini API key in ${INSTALL_DIR}/.env"
echo -e "2. Restart services: cd ${INSTALL_DIR} && docker compose restart"
echo -e "3. Access the application at http://localhost:3001"
echo -e "\n${YELLOW}To view logs:${NC}"
echo -e "docker compose logs -f"
echo -e "\n${YELLOW}To update:${NC}"
echo -e "cd ${INSTALL_DIR} && git pull && docker compose up -d --build"
echo -e "\n${YELLOW}To uninstall:${NC}"
echo -e "cd ${INSTALL_DIR} && docker compose down -v && cd .. && rm -rf ${INSTALL_DIR}"