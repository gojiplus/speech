"""
Audio mixing module for the Enhanced Speech Tool.
Handles combining synthesized audio segments into a final audio file.
"""

import logging
from pathlib import Path
import numpy as np
import tempfile

from pydub import AudioSegment

logger = logging.getLogger("EnhancedSpeech.AudioMixer")

class AudioMixer:
    """Class for mixing and combining audio segments."""
    
    def __init__(self, temp_dir):
        """
        Initialize the audio mixer.
        
        Args:
            temp_dir: Directory for temporary files
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized AudioMixer with temp_dir={temp_dir}")
    
    def mix(self, segments, output_path, maintain_timing=True):
        """
        Mix audio segments into a single file.
        
        Args:
            segments: List of segments with audio file paths
            output_path: Path to the output file
            maintain_timing: Whether to maintain original timing with silence
            
        Returns:
            Path to the output file
        """
        logger.info(f"Mixing {len(segments)} audio segments to {output_path}")
        
        # Create combined audio
        combined = AudioSegment.silent(duration=0)
        
        # Track timing for maintaining original spacing
        last_end_time = 0
        
        # Process each segment
        for i, segment in enumerate(segments):
            try:
                # Load audio file
                audio_file = segment.get("audio_file")
                if not audio_file:
                    logger.warning(f"Segment {i} has no audio file, skipping")
                    continue
                
                audio = AudioSegment.from_file(audio_file)
                
                if maintain_timing:
                    # Add silence to maintain original timing
                    start_time = segment.get("start", last_end_time)
                    silence_duration = max(0, (start_time - last_end_time) * 1000)  # Convert to ms
                    
                    if silence_duration > 0:
                        combined += AudioSegment.silent(duration=silence_duration)
                    
                    # Update last end time
                    last_end_time = segment.get("end", start_time + (len(audio) / 1000))
                
                # Add audio to combined output
                combined += audio
                
            except Exception as e:
                logger.error(f"Error processing segment {i}: {e}")
                # Continue with next segment
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export final audio
        combined.export(
            str(output_path),
            format="mp3",
            bitrate="192k",
            tags={
                "title": output_path.stem,
                "artist": "Enhanced Speech Tool",
                "album": "Speech Enhancement",
                "comment": "Generated with Enhanced Speech Tool"
            }
        )
        
        logger.info(f"Successfully mixed audio segments into {output_path}")
        return str(output_path)
    
    def create_audio_visualization(self, audio_path, output_path=None):
        """
        Create a visualization of an audio file.
        This is a placeholder for a future feature.
        
        Args:
            audio_path: Path to the audio file
            output_path: Path to the output image file
            
        Returns:
            Path to the output image file
        """
        logger.info(f"Creating audio visualization for {audio_path}")
        
        # This is a placeholder - in a real implementation, this would
        # create a waveform or spectrogram visualization
        
        if output_path is None:
            output_path = self.temp_dir / f"{Path(audio_path).stem}_visualization.png"
        
        # Create a simple waveform image
        try:
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            
            # Extract samples
            samples = np.array(audio.get_array_of_samples())
            
            # Here you would use matplotlib to create a waveform visualization
            # For simplicity, we're just creating a placeholder file
            with open(output_path, 'w') as f:
                f.write("Placeholder for audio visualization")
            
            logger.info(f"Created audio visualization at {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error creating audio visualization: {e}")
            return None