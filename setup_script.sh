#!/bin/bash
# setup_speech_enhancer.sh - Setup script for Speech Clarity Enhancer

echo "=== Speech Clarity Enhancer Setup ==="
echo "This script will install the required dependencies for the Speech Clarity Enhancer."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✓ Homebrew is already installed"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing Python 3..."
    brew install python
else
    echo "✓ Python 3 is already installed"
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed. Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
else
    echo "✓ pip is already installed"
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg is not installed. Installing ffmpeg..."
    brew install ffmpeg
else
    echo "✓ ffmpeg is already installed"
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv speech_enhancer_env

# Activate virtual environment
echo "Activating virtual environment..."
source speech_enhancer_env/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install yt-dlp openai-whisper pydub tqdm requests

echo ""
echo "=== Setup Complete! ==="
echo "To use the Speech Clarity Enhancer:"
echo "1. Activate the virtual environment: source speech_enhancer_env/bin/activate"
echo "2. Run the script: python speech_clarity_enhancer.py -yt <youtube-url> -v american"
echo ""
echo "For help: python speech_clarity_enhancer.py --help"
echo ""
