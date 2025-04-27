#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}PDF Comparison Tool - Setup Script${NC}"
echo "=============================="

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
if command -v python3 >/dev/null 2>&1; then
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    echo "Found Python version: $python_version"
else
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
else
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Virtual environment created successfully.${NC}"
    else
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Virtual environment activated.${NC}"
else
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
else
    echo -e "${RED}Failed to install dependencies.${NC}"
    exit 1
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
directories=(
    "data"
    "logs"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "Created directory: $dir"
    else
        echo "Directory already exists: $dir"
    fi
done

# Create configuration file
echo -e "\n${YELLOW}Setting up configuration...${NC}"
if [ ! -f "config/settings.yaml" ]; then
    cp config/settings.yaml.example config/settings.yaml
    echo -e "${GREEN}Created configuration file from example.${NC}"
    echo -e "${YELLOW}Please edit config/settings.yaml with your settings.${NC}"
else
    echo "Configuration file already exists."
fi

# Run setup verification
echo -e "\n${YELLOW}Running setup verification...${NC}"
python test_setup.py
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Setup completed successfully!${NC}"
    echo -e "\nTo start using the PDF Comparison Tool:"
    echo "1. Edit config/settings.yaml with your settings"
    echo "2. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo "3. Run the application:"
    echo "   python src/main.py"
else
    echo -e "\n${RED}Setup verification failed. Please check the output above for details.${NC}"
    exit 1
fi

# Create .gitignore
echo -e "\n${YELLOW}Creating .gitignore...${NC}"
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Distribution / packaging
dist/
build/
*.egg-info/

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
coverage.xml
*.cover
.pytest_cache/

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Configuration
config/settings.yaml

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOL

echo -e "${GREEN}Created .gitignore file${NC}"

# Make test_setup.py executable
chmod +x test_setup.py
echo -e "${GREEN}Made test_setup.py executable${NC}"

echo -e "\n${GREEN}Setup complete!${NC}"
echo "=============================="
echo -e "Next steps:"
echo "1. Edit config/settings.yaml with your settings"
echo "2. Set up your Slack webhook URL for notifications"
echo "3. Configure your offer and invoice folder paths"
echo -e "\nTo start the application:"
echo "source venv/bin/activate"
echo "python src/main.py"
