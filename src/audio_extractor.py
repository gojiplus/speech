"""
Audio extraction module for the Enhanced Speech Tool.
Handles extracting audio from YouTube videos, files, and URLs.
"""

import os
import logging
from pathlib import Path
import subprocess

import yt_dlp
from pydub import AudioSegment

logger = logging.getLogger("EnhancedSpeech.AudioExtractor")

class AudioExtractor:
    """Class for extracting audio from various sources."""
    
    def __init__(self, temp_dir):
        """
        Initialize the audio extractor.
        
        Args:
            temp_dir: Directory to store temporary files
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def extract(self, source, source_type="youtube"):
        """
        Extract audio from a source.
        
        Args:
            source: YouTube URL, file path, or direct audio URL
            source_type: Type of source ('youtube', 'file', or 'url')
            
        Returns:
            Tuple of (path to extracted audio file, title)
        """
        if source_type == "youtube":
            return self._extract_from_youtube(source)
        elif source_type == "file":
            return self._extract_from_file(source)
        elif source_type == "url":
            return self._extract_from_url(source)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def _extract_from_youtube(self, youtube_url):
        """
        Extract audio from a YouTube video.
        
        Args:
            youtube_url: YouTube video URL
            
        Returns:
            Tuple of (path to extracted audio file, video title)
        """
        logger.info(f"Extracting audio from YouTube: {youtube_url}")
        
        output_file = self.temp_dir / "audio.mp3"
        
        # Options for yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(output_file).replace(".mp3", ""),
            'quiet': True,
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                video_title = info_dict.get('title', 'youtube_video')
            
            logger.info(f"Successfully downloaded audio: {video_title}")
            return str(output_file), video_title
        
        except Exception as e:
            logger.error(f"Error downloading YouTube audio: {e}")
            raise
    
    def _extract_from_file(self, file_path):
        """
        Extract audio from a local file.
        
        Args:
            file_path: Path to the local audio file
            
        Returns:
            Tuple of (path to extracted audio file, file name)
        """
        logger.info(f"Loading audio from file: {file_path}")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        output_file = self.temp_dir / "audio.mp3"
        
        # Convert to mp3 if necessary
        try:
            audio = AudioSegment.from_file(str(file_path))
            audio.export(str(output_file), format="mp3")
            
            logger.info(f"Successfully loaded audio file")
            return str(output_file), file_path.name
        
        except Exception as e:
            logger.error(f"Error loading audio file: {e}")
            raise
    
    def _extract_from_url(self, audio_url):
        """
        Extract audio from a direct URL.
        
        Args:
            audio_url: Direct URL to an audio file
            
        Returns:
            Tuple of (path to extracted audio file, file name)
        """
        logger.info(f"Downloading audio from URL: {audio_url}")
        
        output_file = self.temp_dir / "audio.mp3"
        
        try:
            # Use curl or wget to download the file
            subprocess.run([
                "curl", "-L", "-s", audio_url, "-o", str(output_file)
            ], check=True)
            
            # Get the filename from the URL
            file_name = audio_url.split("/")[-1].split("?")[0] or "audio_from_url"
            
            logger.info(f"Successfully downloaded audio from URL")
            return str(output_file), file_name
        
        except Exception as e:
            logger.error(f"Error downloading audio from URL: {e}")
            raise