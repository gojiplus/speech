"""
Transcription module for the Enhanced Speech Tool.
Uses OpenAI's Whisper for local speech-to-text conversion.
"""

import logging
import os
from pathlib import Path
import json
import time

import whisper
import torch
import numpy as np

logger = logging.getLogger("EnhancedSpeech.Transcriber")

class WhisperTranscriber:
    """
    Class for transcribing audio files using OpenAI's Whisper.
    """
    
    def __init__(self, model_size="base", device=None, language="en", compute_type="float16"):
        """
        Initialize the transcriber.
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device to use for inference ("cpu", "cuda", or None for auto-detection)
            language: Language code for transcription
            compute_type: Computation type ("float16", "float32", "int8")
        """
        self.model_size = model_size
        self.language = language
        self.compute_type = compute_type
        
        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.model = None
        logger.info(f"Initialized WhisperTranscriber with model_size={model_size}, device={self.device}, language={language}")
    
    def _load_model(self):
        """Load the Whisper model if not already loaded."""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            try:
                self.model = whisper.load_model(self.model_size, device=self.device)
                logger.info(f"Successfully loaded Whisper model")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
                raise
    
    def transcribe(self, audio_path, word_timestamps=True, task="transcribe"):
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to the audio file
            word_timestamps: Whether to generate timestamps for individual words
            task: Task to perform ("transcribe" or "translate")
            
        Returns:
            Dictionary with transcription result
        """
        logger.info(f"Transcribing audio: {audio_path}")
        start_time = time.time()
        
        # Load model if not loaded
        self._load_model()
        
        try:
            # Set options
            options = {
                "fp16": False if self.device == "cpu" else True,
                "language": self.language,
                "task": task,
                "word_timestamps": word_timestamps
            }
            
            # Transcribe audio
            result = self.model.transcribe(audio_path, **options)
            
            # Add some information about the transcription
            num_segments = len(result.get("segments", []))
            total_duration = result.get("segments", [{}])[-1].get("end", 0) if num_segments > 0 else 0
            
            elapsed_time = time.time() - start_time
            logger.info(f"Transcription complete: {num_segments} segments, {total_duration:.2f} seconds audio")
            logger.info(f"Processing took {elapsed_time:.2f} seconds ({total_duration/elapsed_time:.2f}x real-time)")
            
            # Show a sample of the transcription
            if num_segments > 0:
                sample = result["segments"][0]["text"]
                if len(sample) > 100:
                    sample = sample[:100] + "..."
                logger.info(f"Sample transcription: {sample}")
            
            # Save transcription to file (optional)
            self._save_transcription(result, audio_path)
            
            return result
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def _save_transcription(self, result, audio_path, output_dir=None):
        """
        Save transcription to file.
        
        Args:
            result: Transcription result
            audio_path: Path to the audio file
            output_dir: Directory to save transcription to (default: same as audio file)
        """
        try:
            # Determine output path
            audio_path = Path(audio_path)
            if output_dir is None:
                output_dir = audio_path.parent
            output_dir = Path(output_dir)
            
            # Create directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save transcription to JSON file
            json_path = output_dir / f"{audio_path.stem}_transcription.json"
            with open(json_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Save transcript to text file
            text_path = output_dir / f"{audio_path.stem}_transcript.txt"
            with open(text_path, 'w') as f:
                f.write(result["text"])
                f.write("\n\n--- Segments ---\n\n")
                for i, segment in enumerate(result.get("segments", [])):
                    f.write(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}\n")
            
            logger.debug(f"Saved transcription to {json_path} and {text_path}")
        
        except Exception as e:
            logger.warning(f"Error saving transcription: {e}")


class TranscriptionEnhancer:
    """Class for enhancing transcription with additional features."""
    
    def __init__(self, language_model=None, confidence_threshold=0.5):
        """
        Initialize the transcription enhancer.
        
        Args:
            language_model: Optional language model for enhancing transcription quality
            confidence_threshold: Confidence threshold for word filtering
        """
        self.language_model = language_model
        self.confidence_threshold = confidence_threshold
        logger.info(f"Initialized TranscriptionEnhancer with confidence_threshold={confidence_threshold}")
    
    def enhance(self, transcription):
        """
        Enhance a transcription with additional features.
        
        Args:
            transcription: Raw transcription result from Whisper
            
        Returns:
            Enhanced transcription
        """
        logger.info("Enhancing transcription...")
        
        # Filter low-confidence words if available
        if "segments" in transcription:
            for segment in transcription["segments"]:
                if "words" in segment:
                    segment["words"] = [
                        word for word in segment["words"]
                        if word.get("confidence", 1.0) >= self.confidence_threshold
                    ]
        
        # Apply language model rescoring if available
        if self.language_model and "segments" in transcription:
            transcription = self._apply_language_model(transcription)
        
        # Normalize punctuation
        transcription = self._normalize_punctuation(transcription)
        
        logger.info("Transcription enhancement complete")
        return transcription
    
    def _apply_language_model(self, transcription):
        """
        Apply language model rescoring to improve transcription quality.
        
        Args:
            transcription: Transcription result
            
        Returns:
            Enhanced transcription
        """
        # This is a placeholder for language model rescoring
        # In a real implementation, this would use a language model
        # to improve the transcription quality
        logger.info("Applying language model rescoring...")
        return transcription
    
    def _normalize_punctuation(self, transcription):
        """
        Normalize punctuation in transcription.
        
        Args:
            transcription: Transcription result
            
        Returns:
            Transcription with normalized punctuation
        """
        # This is a basic punctuation normalization
        if "segments" in transcription:
            for segment in transcription["segments"]:
                # Fix spacing around punctuation
                text = segment["text"]
                text = text.replace(" ,", ",")
                text = text.replace(" .", ".")
                text = text.replace(" !", "!")
                text = text.replace(" ?", "?")
                text = text.replace(" :", ":")
                text = text.replace(" ;", ";")
                
                # Ensure space after punctuation
                text = text.replace(",", ", ")
                text = text.replace(".", ". ")
                text = text.replace("!", "! ")
                text = text.replace("?", "? ")
                text = text.replace(":", ": ")
                text = text.replace(";", "; ")
                
                # Remove double spaces
                text = " ".join(text.split())
                
                segment["text"] = text
            
            # Also update the full text
            transcription["text"] = " ".join(segment["text"] for segment in transcription["segments"])
        
        return transcription


def get_audio_duration(audio_path):
    """
    Get the duration of an audio file in seconds.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Duration in seconds
    """
    try:
        info = whisper.audio.load_audio(audio_path, sr=16000)
        duration = len(info) / 16000
        return duration
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return None