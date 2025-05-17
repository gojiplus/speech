"""
Speech synthesis module for the Enhanced Speech Tool.
Uses Piper TTS for high-quality speech synthesis.
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
import json
import shutil

logger = logging.getLogger("EnhancedSpeech.SpeechSynthesizer")

class PiperTTSSynthesizer:
    """Class for synthesizing speech using Piper TTS."""
    
    def __init__(self, voice="en_US-lessac-medium", speaker=0, models_dir=None):
        """
        Initialize the speech synthesizer.
        
        Args:
            voice: Piper voice model name
            speaker: Speaker ID for multi-speaker models
            models_dir: Directory containing Piper voice models
        """
        self.voice = voice
        self.speaker = speaker
        
        # Set default models directory if not provided
        if models_dir is None:
            self.models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        else:
            self.models_dir = Path(models_dir)
        
        # Verify Piper is installed
        self._check_piper_installation()
        
        logger.info(f"Initialized PiperTTSSynthesizer with voice={voice}, speaker={speaker}")
    
    def _check_piper_installation(self):
        """Check if Piper is installed and download models if needed."""
        # Try to find piper executable
        try:
            result = subprocess.run(
                ["piper", "--help"],
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode != 0:
                logger.warning("Piper not found. Make sure it's installed and in your PATH.")
                logger.warning("Install with: pip install piper-tts")
                raise RuntimeError("Piper TTS not found")
            
        except FileNotFoundError:
            logger.error("Piper executable not found. Please install Piper TTS.")
            logger.error("pip install piper-tts")
            raise RuntimeError("Piper TTS not installed")
        
        # Check for voice models
        voice_path = self.models_dir / f"{self.voice}.onnx"
        if not voice_path.exists():
            logger.warning(f"Voice model not found: {voice_path}")
            logger.warning(f"Attempting to download voice model...")
            
            # Create models directory if it doesn't exist
            self.models_dir.mkdir(parents=True, exist_ok=True)
            
            # Try to download the model
            try:
                subprocess.run(
                    ["piper-download", "--voice", self.voice],
                    check=True
                )
                logger.info(f"Successfully downloaded voice model: {self.voice}")
            except Exception as e:
                logger.error(f"Failed to download voice model: {e}")
                raise RuntimeError(f"Voice model {self.voice} not found and could not be downloaded")
    
    def synthesize(self, segments):
        """
        Synthesize speech for transcription segments.
        
        Args:
            segments: List of processed transcription segments
            
        Returns:
            List of segments with audio file paths
        """
        logger.info(f"Synthesizing speech for {len(segments)} segments")
        
        synthesized_segments = []
        
        # Create temporary directory for synthesized audio
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            
            # Process each segment
            for i, segment in enumerate(segments):
                text = segment["text"].strip()
                start_time = segment["start"]
                end_time = segment["end"]
                
                # Skip empty segments
                if not text:
                    logger.debug(f"Skipping empty segment {i}")
                    continue
                
                # Create output file path
                output_file = temp_dir / f"segment_{i:04d}.wav"
                
                # Synthesize speech
                try:
                    self._synthesize_text(text, output_file)
                    
                    # Add synthesized audio to segment
                    synthesized_segments.append({
                        "text": text,
                        "start": start_time,
                        "end": end_time,
                        "audio_file": str(output_file)
                    })
                    
                except Exception as e:
                    logger.error(f"Error synthesizing segment {i}: {e}")
                    # Continue with next segment if one fails
                    continue
            
            logger.info(f"Successfully synthesized {len(synthesized_segments)} segments")
            
            # Copy the synthesized files to a more persistent location if needed
            # (This is a basic implementation - in a real app, you might want to handle this differently)
            result_segments = []
            for segment in synthesized_segments:
                source_file = Path(segment["audio_file"])
                target_file = Path(tempfile.gettempdir()) / source_file.name
                shutil.copy2(source_file, target_file)
                
                segment_copy = segment.copy()
                segment_copy["audio_file"] = str(target_file)
                result_segments.append(segment_copy)
            
            return result_segments
    
    def _synthesize_text(self, text, output_file):
        """
        Synthesize speech for a text segment.
        
        Args:
            text: Text to synthesize
            output_file: Output audio file path
            
        Returns:
            None
        """
        try:
            # Run Piper to synthesize speech
            process = subprocess.Popen(
                [
                    "piper",
                    "--model", str(self.models_dir / f"{self.voice}.onnx"),
                    "--output_file", str(output_file),
                    "--speaker", str(self.speaker)
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send text to synthesize
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                logger.error(f"Piper synthesis failed: {stderr}")
                raise RuntimeError(f"Speech synthesis failed: {stderr}")
            
            logger.debug(f"Synthesized text: '{text[:50]}...' to {output_file}")
            
        except Exception as e:
            logger.error(f"Error synthesizing text: {e}")
            raise