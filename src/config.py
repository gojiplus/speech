"""
Configuration module for the Enhanced Speech Tool.
Handles loading and managing configuration settings.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("EnhancedSpeech.Config")

class Config:
    """Class for managing configuration settings."""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        # Output settings
        "output_dir": "enhanced_audio",
        
        # Whisper settings
        "whisper_model": "base",  # tiny, base, small, medium, large
        "device": None,  # None for auto-detect, "cpu", or "cuda"
        
        # Text processing settings
        "remove_disfluencies": True,
        "simplify_language": False,
        
        # TTS settings
        "tts_engine": "piper",  # piper, macos, espeak
        "voice": "en_US-lessac-medium",  # For Piper
        "speaker": 0,  # For multi-speaker models
        "tts_models_dir": None,  # None for default location
        
        # Audio settings
        "maintain_timing": True,
        "output_format": "mp3",
        "output_bitrate": "192k",
        
        # Experimental features
        "experimental": {
            "enable_speaker_diarization": False,
            "enable_language_model_rescoring": False
        }
    }
    
    def __init__(self, config_path=None):
        """
        Initialize the configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load default configuration
        self._config = self.DEFAULT_CONFIG.copy()
        
        # Load configuration from file if provided
        if config_path is not None:
            self._load_from_file(config_path)
        
        # Load configuration from environment variables
        self._load_from_env()
        
        logger.info(f"Initialized Config with {len(self._config)} settings")
    
    def _load_from_file(self, config_path):
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            
            # Update configuration with values from file
            self._update_config(file_config)
            logger.info(f"Loaded configuration from {config_path}")
        
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Map environment variables to configuration keys
        env_mapping = {
            "ESH_OUTPUT_DIR": "output_dir",
            "ESH_WHISPER_MODEL": "whisper_model",
            "ESH_DEVICE": "device",
            "ESH_REMOVE_DISFLUENCIES": "remove_disfluencies",
            "ESH_SIMPLIFY_LANGUAGE": "simplify_language",
            "ESH_TTS_ENGINE": "tts_engine",
            "ESH_VOICE": "voice",
            "ESH_SPEAKER": "speaker",
            "ESH_TTS_MODELS_DIR": "tts_models_dir",
            "ESH_MAINTAIN_TIMING": "maintain_timing",
            "ESH_OUTPUT_FORMAT": "output_format",
            "ESH_OUTPUT_BITRATE": "output_bitrate"
        }
        
        # Update configuration with values from environment variables
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Convert boolean strings to booleans
                if value.lower() in ["true", "yes", "1"]:
                    value = True
                elif value.lower() in ["false", "no", "0"]:
                    value = False
                
                # Convert numeric strings to numbers
                try:
                    if value.isdigit():
                        value = int(value)
                    elif value.replace(".", "", 1).isdigit():
                        value = float(value)
                except (AttributeError, ValueError):
                    pass
                
                # Update configuration
                self._config[config_key] = value
                logger.debug(f"Loaded configuration from environment: {config_key}={value}")
    
    def _update_config(self, new_config):
        """
        Update configuration with new values.
        
        Args:
            new_config: New configuration values
        """
        for key, value in new_config.items():
            if isinstance(value, dict) and key in self._config and isinstance(self._config[key], dict):
                # Recursively update nested dictionaries
                self._config[key].update(value)
            else:
                # Update value
                self._config[key] = value
    
    def save(self, config_path):
        """
        Save configuration to a file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            
            logger.info(f"Saved configuration to {config_path}")
        
        except Exception as e:
            logger.error(f"Error saving configuration to {config_path}: {e}")
    
    def __getattr__(self, name):
        """
        Get configuration attribute.
        
        Args:
            name: Attribute name
            
        Returns:
            Configuration value
        """
        if name in self._config:
            return self._config[name]
        else:
            raise AttributeError(f"Configuration has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        """
        Set configuration attribute.
        
        Args:
            name: Attribute name
            value: Attribute value
        """
        if name == "_config":
            # Set the internal configuration dictionary
            super().__setattr__(name, value)
        elif name in self._config:
            # Update configuration value
            self._config[name] = value
        else:
            # Set attribute normally
            super().__setattr__(name, value)