# Enhanced Speech Clarity Tool

A tool for converting difficult-to-understand speech (such as accented English) into clear, pleasant voices with disfluency removal.

## Features

- Extract audio from YouTube videos or local files
- Transcribe speech with high accuracy using OpenAI's Whisper (locally)
- Remove speech disfluencies (um, uh, false starts, repetitions)
- Convert to natural-sounding speech using high-quality neural TTS
- Maintain the original timing and pacing of the conversation

## Requirements

- Python 3.8 or higher
- FFmpeg
- 4GB+ RAM for transcription
- 500MB+ disk space for models

## Installation

### Quick Setup (Recommended)

Run the provided setup script, which will install all required dependencies and download the necessary models:

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Manual Installation

If you prefer to install manually:

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install Python dependencies:
   ```bash
   pip install yt-dlp pydub tqdm openai-whisper piper-tts torch
   ```

3. Download the TTS voice model:
   ```bash
   piper-download --voice en_US-lessac-medium
   ```

## Usage

### Process a YouTube Video

```bash
python enhanced_speech_tool.py -yt "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

### Process a Local Audio File

```bash
python enhanced_speech_tool.py -f "path/to/audio/file.mp3"
```

### Command Line Options

- `-yt, --youtube`: YouTube URL
- `-f, --file`: Local audio file path
- `-u, --url`: Direct audio URL
- `-c, --config`: Path to configuration file
- `-v, --voice`: Voice to use for synthesis
- `--no-disfluencies`: Remove disfluencies (um, uh, etc.)
- `--simplify`: Simplify language for easier understanding
- `-o, --output-dir`: Output directory

## Voice Options

Several high-quality voices are available through Piper TTS:

- `en_US-lessac-medium`: Clear American English (default)
- `en_GB-alba-medium`: British English
- `en_US-ryan-high`: Male American voice
- `en_AU-sydney-medium`: Australian English

## Configuration

You can customize the tool's behavior by creating a configuration file. Example:

```json
{
    "output_dir": "enhanced_audio",
    "whisper_model": "base",
    "device": null,
    "remove_disfluencies": true,
    "simplify_language": false,
    "tts_engine": "piper",
    "voice": "en_US-lessac-medium",
    "maintain_timing": true
}
```

## Project Structure

```
enhanced_speech_tool/
├── enhanced_speech_tool.py     # Main script
├── setup.sh                    # Setup script
├── config/                     # Configuration files
│   └── default.json            # Default configuration
├── src/                        # Source code
│   ├── audio_extractor.py      # Audio extraction module
│   ├── transcriber.py          # Speech transcription module
│   ├── text_processor.py       # Text processing module
│   ├── speech_synthesizer.py   # Speech synthesis module
│   ├── audio_mixer.py          # Audio mixing module
│   └── config.py               # Configuration module
└── enhanced_audio/             # Output directory
```

## Limitations

- Whisper transcription may not be perfect for all accents or poor audio quality
- Neural TTS voices require downloading models (~200MB per voice)
- Processing long audio files (>30 minutes) can take significant time

## Credits

This tool uses the following open-source libraries:

- [OpenAI Whisper](https://github.com/openai/whisper) for transcription
- [Piper TTS](https://github.com/rhasspy/piper) for speech synthesis
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube audio extraction
- [PyDub](https://github.com/jiaaro/pydub) for audio processing