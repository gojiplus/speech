#!/bin/bash
# setup.sh - Setup script for the Enhanced Speech Tool

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Enhanced Speech Tool Setup ===${NC}"
echo -e "This script will install all required dependencies for the Enhanced Speech Tool."

# Create a clean Python virtual environment
create_venv() {
    echo -e "\n${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv .venv
    
    # Activate virtual environment
    if [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment created and activated${NC}"
    else
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    fi
}

# Install required system dependencies
install_system_deps() {
    echo -e "\n${YELLOW}Installing system dependencies...${NC}"
    
    # Check operating system
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo -e "Detected macOS system"
        
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            echo -e "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        else
            echo -e "${GREEN}✓ Homebrew already installed${NC}"
        fi
        
        # Install dependencies with Homebrew
        echo -e "Installing dependencies with Homebrew..."
        brew install ffmpeg python cmake
        
        echo -e "${GREEN}✓ System dependencies installed${NC}"
        
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo -e "Detected Linux system"
        
        # Try to detect distribution
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            echo -e "Installing dependencies with apt..."
            sudo apt-get update
            sudo apt-get install -y ffmpeg python3-pip python3-venv build-essential cmake
        elif command -v dnf &> /dev/null; then
            # Fedora
            echo -e "Installing dependencies with dnf..."
            sudo dnf install -y ffmpeg python3-pip python3-devel gcc cmake
        elif command -v pacman &> /dev/null; then
            # Arch Linux
            echo -e "Installing dependencies with pacman..."
            sudo pacman -S ffmpeg python python-pip cmake
        else
            echo -e "${RED}Unsupported Linux distribution. Please install the following dependencies manually:${NC}"
            echo -e "- ffmpeg"
            echo -e "- Python 3.8 or higher"
            echo -e "- pip"
            echo -e "- build tools (gcc, cmake)"
            exit 1
        fi
        
        echo -e "${GREEN}✓ System dependencies installed${NC}"
        
    else
        echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
        echo -e "Please install the required dependencies manually:"
        echo -e "- ffmpeg"
        echo -e "- Python 3.8 or higher"
        echo -e "- pip"
        echo -e "- build tools (gcc, cmake)"
        exit 1
    fi
}

# Install Python dependencies
install_python_deps() {
    echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install core dependencies
    pip install yt-dlp \
                pydub \
                tqdm \
                openai-whisper \
                torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    
    echo -e "${GREEN}✓ Core Python dependencies installed${NC}"
    
    # Install Piper TTS for high-quality speech synthesis
    echo -e "\n${YELLOW}Installing Piper TTS...${NC}"
    pip install piper-tts
    
    echo -e "${GREEN}✓ Piper TTS installed${NC}"
}

# Create project structure
create_project_structure() {
    echo -e "\n${YELLOW}Creating project structure...${NC}"
    
    # Create directories
    mkdir -p enhanced_audio
    mkdir -p src
    mkdir -p config
    
    # Move source files to src directory
    if [ -f audio_extractor.py ]; then
        mv audio_extractor.py src/
    fi
    if [ -f transcriber.py ]; then
        mv transcriber.py src/
    fi
    if [ -f text_processor.py ]; then
        mv text_processor.py src/
    fi
    if [ -f speech_synthesizer.py ]; then
        mv speech_synthesizer.py src/
    fi
    if [ -f audio_mixer.py ]; then
        mv audio_mixer.py src/
    fi
    if [ -f config.py ]; then
        mv config.py src/
    fi
    
    # Create __init__.py files
    touch src/__init__.py
    
    echo -e "${GREEN}✓ Project structure created${NC}"
}

# Create default configuration
create_default_config() {
    echo -e "\n${YELLOW}Creating default configuration...${NC}"
    
    # Create default configuration file
    cat > config/default.json << EOL
{
    "output_dir": "enhanced_audio",
    "whisper_model": "base",
    "device": null,
    "remove_disfluencies": true,
    "simplify_language": false,
    "tts_engine": "piper",
    "voice": "en_US-lessac-medium",
    "speaker": 0,
    "maintain_timing": true,
    "output_format": "mp3",
    "output_bitrate": "192k"
}
EOL
    
    echo -e "${GREEN}✓ Default configuration created${NC}"
}

# Download TTS models
download_tts_models() {
    echo -e "\n${YELLOW}Downloading TTS models...${NC}"
    
    # Download Piper voice models
    piper-download --voice en_US-lessac-medium
    
    echo -e "${GREEN}✓ TTS models downloaded${NC}"
}

# Main setup function
main() {
    # Check Python version
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "Python version: $python_version"
    
    # Check if Python version is 3.8 or higher
    major=$(echo $python_version | cut -d. -f1)
    minor=$(echo $python_version | cut -d. -f2)
    
    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        echo -e "${RED}Error: Python 3.8 or higher is required${NC}"
        exit 1
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Create virtual environment
    create_venv
    
    # Install Python dependencies
    install_python_deps
    
    # Create project structure
    create_project_structure
    
    # Create default configuration
    create_default_config
    
    # Download TTS models
    download_tts_models
    
    echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
    echo -e "To use the Enhanced Speech Tool:"
    echo -e "1. Activate the virtual environment: ${YELLOW}source .venv/bin/activate${NC}"
    echo -e "2. Run the tool: ${YELLOW}python enhanced_speech_tool.py -yt \"https://www.youtube.com/watch?v=YOUR_VIDEO_ID\" -v american${NC}"
    echo -e "\nFor help and options: ${YELLOW}python enhanced_speech_tool.py --help${NC}"
}

# Run the setup
main
