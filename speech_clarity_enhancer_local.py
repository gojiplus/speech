# Speech Clarity Enhancer - Local Implementation
# A simple tool to convert difficult-to-understand speech to clear voices
# For macOS systems

import os
import sys
import argparse
import subprocess
import tempfile
import json
from pathlib import Path
import threading
import queue
import time
import re

# Requirements:
# pip install yt-dlp whisper openai-whisper pydub tqdm requests

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp not installed. Please install it with 'pip install yt-dlp'")
    sys.exit(1)

try:
    import whisper
except ImportError:
    print("Error: whisper not installed. Please install it with 'pip install openai-whisper'")
    sys.exit(1)

try:
    from pydub import AudioSegment
    from pydub.playback import play
except ImportError:
    print("Error: pydub not installed. Please install it with 'pip install pydub'")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("Error: tqdm not installed. Please install it with 'pip install tqdm'")
    sys.exit(1)

# Terminal colors for better output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Main class for the Speech Clarity Enhancer
class SpeechClarityEnhancer:
    def __init__(self, output_dir="enhanced_audio"):
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Initialize Whisper model to None (will load on demand)
        self.whisper_model = None
        
        print(f"{Colors.HEADER}Speech Clarity Enhancer{Colors.ENDC}")
        print(f"Temporary files will be stored in: {self.temp_dir}")
        print(f"Enhanced audio will be saved to: {os.path.abspath(self.output_dir)}")
    
    def download_youtube_audio(self, youtube_url):
        """Download audio from a YouTube video"""
        print(f"\n{Colors.BLUE}[1/4] Downloading audio from YouTube...{Colors.ENDC}")
        
        output_file = os.path.join(self.temp_dir, "audio.mp3")
        
        # Options for yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_file.replace(".mp3", ""),
            'quiet': False,
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                video_title = info_dict.get('title', 'youtube_video')
                
            print(f"{Colors.GREEN}✓ Successfully downloaded audio from: {video_title}{Colors.ENDC}")
            return output_file, video_title
        except Exception as e:
            print(f"{Colors.RED}Error downloading YouTube audio: {str(e)}{Colors.ENDC}")
            sys.exit(1)
    
    def load_local_audio(self, audio_path):
        """Load audio from a local file"""
        print(f"\n{Colors.BLUE}[1/4] Loading local audio file...{Colors.ENDC}")
        
        if not os.path.exists(audio_path):
            print(f"{Colors.RED}Error: Audio file not found: {audio_path}{Colors.ENDC}")
            sys.exit(1)
        
        output_file = os.path.join(self.temp_dir, "audio.mp3")
        
        # Convert to mp3 if necessary
        try:
            audio = AudioSegment.from_file(audio_path)
            audio.export(output_file, format="mp3")
            
            print(f"{Colors.GREEN}✓ Successfully loaded audio file{Colors.ENDC}")
            return output_file, os.path.basename(audio_path)
        except Exception as e:
            print(f"{Colors.RED}Error loading audio file: {str(e)}{Colors.ENDC}")
            sys.exit(1)
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio using OpenAI's Whisper"""
        print(f"\n{Colors.BLUE}[2/4] Transcribing audio with Whisper...{Colors.ENDC}")
        print("This may take a while depending on the length of the audio.")
        
        # Load Whisper model if not already loaded
        if self.whisper_model is None:
            print(f"{Colors.YELLOW}Loading Whisper model (this happens only once)...{Colors.ENDC}")
            self.whisper_model = whisper.load_model("base")
        
        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_file)
            
            # Save transcript to file
            transcript_file = os.path.join(self.temp_dir, "transcript.json")
            with open(transcript_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"{Colors.GREEN}✓ Successfully transcribed audio{Colors.ENDC}")
            
            # Print a sample of the transcript
            sample_text = result["text"][:150] + "..." if len(result["text"]) > 150 else result["text"]
            print(f"\n{Colors.YELLOW}Sample transcript:{Colors.ENDC}")
            print(f"{sample_text}")
            
            return result
        except Exception as e:
            print(f"{Colors.RED}Error transcribing audio: {str(e)}{Colors.ENDC}")
            sys.exit(1)
    
    def segment_audio(self, audio_file, transcription_result):
        """Segment audio based on transcription timestamps"""
        print(f"\n{Colors.BLUE}[3/4] Segmenting audio...{Colors.ENDC}")
        
        segments = transcription_result.get("segments", [])
        if not segments:
            print(f"{Colors.RED}Error: No segments found in transcription{Colors.ENDC}")
            sys.exit(1)
        
        try:
            # Load the audio file
            audio = AudioSegment.from_file(audio_file)
            
            # Create segments directory
            segments_dir = os.path.join(self.temp_dir, "segments")
            os.makedirs(segments_dir, exist_ok=True)
            
            segment_files = []
            
            for i, segment in enumerate(tqdm(segments, desc="Segmenting audio")):
                start_ms = int(segment["start"] * 1000)
                end_ms = int(segment["end"] * 1000)
                text = segment["text"]
                
                # Extract segment
                audio_segment = audio[start_ms:end_ms]
                
                # Save segment
                segment_file = os.path.join(segments_dir, f"segment_{i:04d}.mp3")
                audio_segment.export(segment_file, format="mp3")
                
                segment_files.append({
                    "file": segment_file,
                    "text": text,
                    "start": segment["start"],
                    "end": segment["end"]
                })
            
            print(f"{Colors.GREEN}✓ Successfully segmented audio into {len(segment_files)} parts{Colors.ENDC}")
            return segment_files
        except Exception as e:
            print(f"{Colors.RED}Error segmenting audio: {str(e)}{Colors.ENDC}")
            sys.exit(1)
    
    def synthesize_speech(self, segments, voice_type="macos"):
        """Synthesize speech for each segment using macOS say command"""
        print(f"\n{Colors.BLUE}[4/4] Synthesizing speech with {voice_type} voice...{Colors.ENDC}")
        
        # Create synthesized directory
        synth_dir = os.path.join(self.temp_dir, "synthesized")
        os.makedirs(synth_dir, exist_ok=True)
        
        synthesized_files = []
        
        # Choose voice based on voice type
        if voice_type == "american":
            voice = "Samantha"  # American female
        elif voice_type == "british":
            voice = "Daniel"    # British male
        elif voice_type == "australian":
            voice = "Karen"     # Australian female
        else:
            voice = "Alex"      # Default macOS voice
        
        for i, segment in enumerate(tqdm(segments, desc="Synthesizing speech")):
            text = segment["text"]
            output_file = os.path.join(synth_dir, f"synth_{i:04d}.aiff")
            
            # Clean up text (remove special characters that might confuse say command)
            text = re.sub(r'[^\w\s.,?!-]', '', text)
            
            # Use macOS say command to synthesize speech
            try:
                subprocess.run([
                    "say", 
                    "-v", voice, 
                    "-o", output_file, 
                    text
                ], check=True, capture_output=True)
                
                synthesized_files.append({
                    "file": output_file,
                    "text": text,
                    "start": segment["start"],
                    "end": segment["end"]
                })
            except subprocess.CalledProcessError as e:
                print(f"{Colors.RED}Error synthesizing segment {i}: {e}{Colors.ENDC}")
                print(f"Error details: {e.stderr.decode('utf-8')}")
        
        print(f"{Colors.GREEN}✓ Successfully synthesized {len(synthesized_files)} segments{Colors.ENDC}")
        return synthesized_files
    
    def combine_audio(self, synthesized_files, output_name):
        """Combine synthesized audio segments into a single file"""
        print(f"\n{Colors.BLUE}Combining audio segments...{Colors.ENDC}")
        
        # Create combined audio file
        combined = AudioSegment.empty()
        
        last_end = 0
        
        for segment in tqdm(synthesized_files, desc="Combining segments"):
            # Load the synthesized audio segment
            try:
                audio = AudioSegment.from_file(segment["file"])
                
                # Calculate silence to insert to maintain timing
                start_time = segment["start"]
                silence_duration = max(0, (start_time - last_end) * 1000)  # ms
                
                if silence_duration > 0:
                    combined += AudioSegment.silent(duration=silence_duration)
                
                # Append audio segment
                combined += audio
                
                # Update last end time
                last_end = segment["end"]
            except Exception as e:
                print(f"{Colors.YELLOW}Warning: Could not load segment {segment['file']}: {e}{Colors.ENDC}")
        
        # Sanitize output name
        safe_name = re.sub(r'[^\w\s-]', '', output_name).strip().replace(' ', '_')
        output_file = os.path.join(self.output_dir, f"{safe_name}_enhanced.mp3")
        
        # Export final audio
        combined.export(output_file, format="mp3")
        
        print(f"{Colors.GREEN}✓ Successfully created enhanced audio: {output_file}{Colors.ENDC}")
        return output_file
    
    def process_audio(self, input_source, voice_type="american", is_youtube=False):
        """Process audio from YouTube URL or local file"""
        try:
            # Step 1: Get audio file
            if is_youtube:
                audio_file, title = self.download_youtube_audio(input_source)
            else:
                audio_file, title = self.load_local_audio(input_source)
            
            # Step 2: Transcribe audio
            transcription = self.transcribe_audio(audio_file)
            
            # Step 3: Segment audio
            segments = self.segment_audio(audio_file, transcription)
            
            # Step 4: Synthesize speech
            synthesized = self.synthesize_speech(segments, voice_type)
            
            # Step 5: Combine audio
            output_file = self.combine_audio(synthesized, title)
            
            print(f"\n{Colors.BOLD}{Colors.GREEN}✓ Processing complete!{Colors.ENDC}")
            print(f"Enhanced audio saved to: {output_file}")
            
            # Open the output directory
            subprocess.run(["open", self.output_dir])
            
            return output_file
        except Exception as e:
            print(f"{Colors.RED}Error processing audio: {str(e)}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Speech Clarity Enhancer")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-yt", "--youtube", help="YouTube URL")
    input_group.add_argument("-f", "--file", help="Local audio file path")
    
    parser.add_argument("-v", "--voice", choices=["american", "british", "australian"], 
                      default="american", help="Voice type (default: american)")
    parser.add_argument("-o", "--output-dir", default="enhanced_audio", 
                      help="Output directory (default: enhanced_audio)")
    
    args = parser.parse_args()
    
    enhancer = SpeechClarityEnhancer(output_dir=args.output_dir)
    
    if args.youtube:
        enhancer.process_audio(args.youtube, args.voice, is_youtube=True)
    elif args.file:
        enhancer.process_audio(args.file, args.voice, is_youtube=False)

if __name__ == "__main__":
    main()
