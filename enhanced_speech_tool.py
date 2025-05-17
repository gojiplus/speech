#!/usr/bin/env python3
# enhanced_speech_tool.py - Main module for Enhanced Speech Clarity Tool

import logging
import os
import sys
import tempfile
from pathlib import Path
import argparse
import json
import shutil
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EnhancedSpeech")

# Import modules for processing chain
from src.audio_extractor import AudioExtractor
from src.transcriber import WhisperTranscriber
from src.text_processor import TextProcessor
from src.speech_synthesizer import PiperTTSSynthesizer
from src.audio_mixer import AudioMixer
from src.config import Config

class EnhancedSpeechTool:
    """Main class for the Enhanced Speech Clarity Tool."""
    
    def __init__(self, config_path=None):
        """Initialize the tool with configuration."""
        # Load configuration
        self.config = Config(config_path)
        
        # Create temporary directory for processing
        self.temp_dir = Path(tempfile.mkdtemp())
        logger.info(f"Using temporary directory: {self.temp_dir}")
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.extractor = AudioExtractor(self.temp_dir)
        self.transcriber = WhisperTranscriber(
            model_size=self.config.whisper_model,
            device=self.config.device
        )
        self.text_processor = TextProcessor(
            remove_disfluencies=self.config.remove_disfluencies,
            simplify_language=self.config.simplify_language
        )
        self.synthesizer = PiperTTSSynthesizer(
            voice=self.config.voice,
            speaker=self.config.speaker,
            models_dir=self.config.tts_models_dir
        )
        self.mixer = AudioMixer(self.temp_dir)
    
    def process(self, source, source_type="youtube"):
        """
        Process a source to create enhanced speech.
        
        Args:
            source: YouTube URL, file path, or direct audio URL
            source_type: Type of source ('youtube', 'file', or 'url')
            
        Returns:
            Path to the enhanced audio file
        """
        try:
            # Step 1: Extract audio
            logger.info("Step 1: Extracting audio...")
            audio_path, title = self.extractor.extract(source, source_type)
            logger.info(f"Extracted audio to {audio_path}")
            
            # Step 2: Transcribe audio
            logger.info("Step 2: Transcribing audio...")
            transcription = self.transcriber.transcribe(audio_path)
            
            # Save raw transcription
            raw_transcript_path = self.temp_dir / "raw_transcript.json"
            with open(raw_transcript_path, 'w') as f:
                json.dump(transcription, f, indent=2)
            logger.info(f"Raw transcription saved to {raw_transcript_path}")
            
            # Step 3: Process the transcription (remove disfluencies, etc.)
            logger.info("Step 3: Processing transcription...")
            processed_segments = self.text_processor.process(transcription)
            
            # Save processed transcription
            processed_transcript_path = self.temp_dir / "processed_transcript.json"
            with open(processed_transcript_path, 'w') as f:
                json.dump(processed_segments, f, indent=2)
            logger.info(f"Processed transcription saved to {processed_transcript_path}")
            
            # Step 4: Synthesize speech
            logger.info("Step 4: Synthesizing speech...")
            synthesized_segments = self.synthesizer.synthesize(processed_segments)
            
            # Step 5: Mix audio segments
            logger.info("Step 5: Mixing audio segments...")
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            output_path = self.output_dir / f"{safe_title}_enhanced.mp3"
            
            self.mixer.mix(synthesized_segments, output_path)
            logger.info(f"Enhanced audio saved to {output_path}")
            
            # Also save a text version of the transcript
            text_transcript_path = self.output_dir / f"{safe_title}_transcript.txt"
            with open(text_transcript_path, 'w') as f:
                for segment in processed_segments:
                    f.write(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}\n")
            logger.info(f"Transcript saved to {text_transcript_path}")
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error processing source: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Error cleaning up: {e}")


def main():
    parser = argparse.ArgumentParser(description="Enhanced Speech Clarity Tool")
    
    # Input source arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-yt", "--youtube", help="YouTube URL")
    input_group.add_argument("-f", "--file", help="Local audio file path")
    input_group.add_argument("-u", "--url", help="Direct audio URL")
    
    # Configuration arguments
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("-v", "--voice", help="Voice to use for synthesis")
    parser.add_argument("--no-disfluencies", action="store_true", 
                        help="Remove disfluencies (um, uh, etc.)")
    parser.add_argument("--simplify", action="store_true",
                        help="Simplify language for easier understanding")
    parser.add_argument("-o", "--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = EnhancedSpeechTool(args.config)
    
    # Override configuration with command line arguments
    if args.voice:
        tool.config.voice = args.voice
    if args.no_disfluencies:
        tool.config.remove_disfluencies = True
    if args.simplify:
        tool.config.simplify_language = True
    if args.output_dir:
        tool.config.output_dir = args.output_dir
        tool.output_dir = Path(args.output_dir)
        tool.output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Process input
        if args.youtube:
            output_path = tool.process(args.youtube, "youtube")
        elif args.file:
            output_path = tool.process(args.file, "file")
        elif args.url:
            output_path = tool.process(args.url, "url")
        
        print(f"\nProcessing complete!")
        print(f"Enhanced audio saved to: {output_path}")
        
        # Open the output directory
        if os.name == 'posix':  # macOS or Linux
            os.system(f"open {tool.output_dir}")
        elif os.name == 'nt':   # Windows
            os.system(f"explorer {tool.output_dir}")
    
    finally:
        # Clean up
        tool.cleanup()

if __name__ == "__main__":
    main()
