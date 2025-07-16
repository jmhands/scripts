#!/bin/bash

# Ghost Installation Script for Ubuntu 24.04 LXC Container
# Following official Ghost documentation: https://ghost.org/docs/install/ubuntu/
# Run as root user

set -e  # Exit on any error

echo "=== Ghost Installation Script - Following Official Guide ==="
echo "This script follows the official Ghost installation guide for Ubuntu"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root"
    exit 1
fi

# Variables - you can modify these
SITE_NAME="blog"
MYSQL_ROOT_PASSWORD="password"
DOMAIN="blog.yourdomain.com"  # Change this to your actual domain

print_warning "Before running this script, make sure you have:"
print_warning "1. A registered domain name pointing to this server's IP"
print_warning "2. At least 1GB of memory"
print_warning "3. Updated the variables in this script (MYSQL_ROOT_PASSWORD, DOMAIN)"
echo ""
read -p "Press Enter to continue or Ctrl+C to abort..."

# Step 1: Update packages
print_status "Updating package lists and installed packages"
apt-get update
apt-get upgrade -y

# Step 2: Install NGINX
print_status "Installing NGINX"
apt-get install nginx -y

# Configure firewall if ufw is available
if command -v ufw &> /dev/null; then
    print_status "Configuring firewall for NGINX"
    ufw allow 'Nginx Full'
fi

# Step 3: Install MySQL
print_status "Installing MySQL server"
apt-get install mysql-server -y

# Configure MySQL root user with password
print_status "Configuring MySQL root user"

# Start MySQL service if not running
systemctl start mysql
systemctl enable mysql

# Create Ghost database and user
print_status "Setting up Ghost database"
DB_NAME="ghost"
DB_USER="ghostuser"
DB_PASS=$(openssl rand -base64 18 | tr -dc 'a-zA-Z0-9' | head -c13)

# Configure MySQL root password if needed
if ! mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "SELECT 1;" &>/dev/null 2>&1; then
    if mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY '$MYSQL_ROOT_PASSWORD'; FLUSH PRIVILEGES;" &>/dev/null 2>&1; then
        print_status "MySQL root password configured successfully"
    else
        print_error "Failed to configure MySQL root password"
        exit 1
    fi
fi

# Create Ghost database and user
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';"
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "GRANT ALL ON $DB_NAME.* TO '$DB_USER'@'localhost'; FLUSH PRIVILEGES;"

# Save credentials
{
  echo "Ghost-Credentials"
  echo "Ghost Database User: $DB_USER"
  echo "Ghost Database Password: $DB_PASS"
  echo "Ghost Database Name: $DB_NAME"
} > ~/ghost.creds

print_status "Ghost database configured successfully"

# Step 4: Install Node.js (version 22 LTS - currently supported)
print_status "Installing Node.js 22 LTS"
apt-get install -y ca-certificates curl gnupg
mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

NODE_MAJOR=22
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

apt-get update
apt-get install nodejs -y

# Step 5: Install Ghost-CLI
print_status "Installing Ghost-CLI"
npm install ghost-cli@latest -g

# Step 6: Create Ghost directory and user
print_status "Creating Ghost user and directory"
adduser --disabled-password --gecos "Ghost user" ghost-user
usermod -aG sudo ghost-user
echo "ghost-user ALL=(ALL) NOPASSWD:ALL" | tee /etc/sudoers.d/ghost-user

mkdir -p /var/www/ghost
chown -R ghost-user:ghost-user /var/www/ghost
chmod 775 /var/www/ghost

# Step 7: Install Ghost
print_status "Installing Ghost"
print_warning "Installing Ghost with the following configuration:"
print_warning "- Blog URL: http://localhost:2368 (can be changed later)"
print_warning "- MySQL Database: $DB_NAME"
print_warning "- MySQL User: $DB_USER"
print_warning "- Running on IP: 0.0.0.0 (accessible from outside container)"

# Install Ghost with all parameters specified to avoid prompts
sudo -u ghost-user -H sh -c "cd /var/www/ghost && ghost install --db=mysql --dbhost=localhost --dbuser=$DB_USER --dbpass=$DB_PASS --dbname=$DB_NAME --url=http://localhost:2368 --no-prompt --no-setup-nginx --no-setup-ssl --no-setup-mysql --enable --start --ip 0.0.0.0"

# Clean up sudo permissions
rm -f /etc/sudoers.d/ghost-user

print_status "Ghost installation completed!"
print_status "Ghost is running on: http://localhost:2368"
print_status "You can access your Ghost admin at: http://localhost:2368/ghost"
print_status ""
print_status "Database credentials saved to: ~/ghost.creds"
print_status ""
print_status "To configure your domain later, run:"
print_status "cd /var/www/ghost && sudo -u ghost-user ghost config url https://$DOMAIN"
print_status ""
print_status "Future maintenance commands (run as ghost-user):"
print_status "- ghost help (for available commands)"
print_status "- ghost update (to update Ghost)"
print_status "- ghost restart (to restart Ghost)"
print_status "- ghost stop/start (to stop/start Ghost)"