"""
Text processing module for the Enhanced Speech Tool.
Handles cleaning transcriptions and removing disfluencies.
"""

import logging
import re
import string

logger = logging.getLogger("EnhancedSpeech.TextProcessor")

class TextProcessor:
    """Class for processing transcribed text."""
    
    # Common filler words and verbal disfluencies
    DISFLUENCIES = [
        r'\bum+\b', r'\buh+\b', r'\ber+\b', r'\bah+\b', r'\bmm+\b', 
        r'\blike\b', r'\byou know\b', r'\bI mean\b', r'\bso\b', 
        r'\bactually\b', r'\bbasically\b', r'\bliterally\b',
        r'\bkind of\b', r'\bsort of\b', r'\ba little bit\b',
        r'\bI guess\b', r'\bwell+\b', r'\banyway+s?\b', r'\bright\b'
    ]
    
    # Repeated words or phrases
    REPETITIONS = [
        r'(\b\w+\b)(\s+\1\b)+'  # Matches repeated words
    ]
    
    # False starts and abandoned phrases
    FALSE_STARTS = [
        r'\b(I|we|they|he|she) (was|were|is|am|are|have|had) (going to|about to)( \w+)+ but\b',
        r"\b(I|we|they|he|she) (don't|doesn't|didn't) (mean|think|want|like)( \w+)+ (I|we|they|he|she) (mean|think|want|like)\b"
    ]
    
    def __init__(self, remove_disfluencies=True, simplify_language=False):
        """
        Initialize the text processor.
        
        Args:
            remove_disfluencies: Whether to remove speech disfluencies
            simplify_language: Whether to simplify language for easier understanding
        """
        self.remove_disfluencies = remove_disfluencies
        self.simplify_language = simplify_language
        logger.info(f"Initialized TextProcessor with remove_disfluencies={remove_disfluencies}, simplify_language={simplify_language}")
    
    def process(self, transcription):
        """
        Process a transcription.
        
        Args:
            transcription: Transcription result from Whisper
            
        Returns:
            List of processed segments
        """
        logger.info(f"Processing transcription with {len(transcription.get('segments', []))} segments")
        
        # Extract segments
        segments = transcription.get("segments", [])
        
        # Process each segment
        processed_segments = []
        for segment in segments:
            processed_text = segment["text"]
            
            # Apply text processing
            if self.remove_disfluencies:
                processed_text = self._remove_disfluencies(processed_text)
            
            if self.simplify_language:
                processed_text = self._simplify_language(processed_text)
            
            # Only include non-empty segments
            if processed_text.strip():
                processed_segments.append({
                    "text": processed_text,
                    "start": segment["start"],
                    "end": segment["end"],
                })
        
        # Log processing stats
        original_word_count = sum(len(s["text"].split()) for s in segments)
        processed_word_count = sum(len(s["text"].split()) for s in processed_segments)
        reduction_percent = 100 * (original_word_count - processed_word_count) / original_word_count if original_word_count > 0 else 0
        
        logger.info(f"Processed transcription: {original_word_count} → {processed_word_count} words ({reduction_percent:.1f}% reduction)")
        
        return processed_segments
    
    def _remove_disfluencies(self, text):
        """
        Remove speech disfluencies from text.
        
        Args:
            text: Text to process
            
        Returns:
            Cleaned text
        """
        # Remember original text for comparison
        original_text = text
        
        # Remove disfluencies
        for pattern in self.DISFLUENCIES:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        # Remove repetitions
        for pattern in self.REPETITIONS:
            text = re.sub(pattern, r'\1', text)
        
        # Remove false starts
        for pattern in self.FALSE_STARTS:
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)
            for match in matches:
                # Find the part after "but" or "I mean", etc.
                full_match = match.group(0)
                split_point = re.search(r'\b(but|I mean|I think)\b', full_match, flags=re.IGNORECASE)
                if split_point:
                    replacement = full_match[split_point.start():]
                    text = text.replace(full_match, replacement)
        
        # Fix spacing and punctuation
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # Capitalize first letter of sentences
        text = self._capitalize_sentences(text)
        
        # Log changes if significant
        if len(text.split()) < len(original_text.split()) * 0.8:
            logger.debug(f"Significant disfluency removal: {len(original_text.split())} → {len(text.split())} words")
        
        return text.strip()
    
    def _simplify_language(self, text):
        """
        Simplify language for easier understanding.
        This is a placeholder for more sophisticated language simplification.
        
        Args:
            text: Text to process
            
        Returns:
            Simplified text
        """
        # This is a placeholder - in a real implementation, this would use
        # a language model to simplify vocabulary and sentence structures
        
        # Here's a very basic implementation that just replaces some complex words
        complex_words = {
            r'\butilize\b': 'use',
            r'\bprocure\b': 'get',
            r'\boptimal\b': 'best',
            r'\bpurchase\b': 'buy',
            r'\bsufficient\b': 'enough',
            r'\brequire\b': 'need',
            r'\bobligation\b': 'duty',
            r'\bterminat(e|ion)\b': 'end',
            r'\binitiate\b': 'start',
            r'\bfinaliz(e|ed)\b': 'finish',
            r'\bsubsequent(ly)?\b': 'later',
        }
        
        for complex_word, simple_word in complex_words.items():
            text = re.sub(complex_word, simple_word, text, flags=re.IGNORECASE)
        
        return text
    
    def _capitalize_sentences(self, text):
        """
        Capitalize the first letter of each sentence.
        
        Args:
            text: Text to process
            
        Returns:
            Text with capitalized sentences
        """
        # Split text into sentences
        sentences = re.split(r'([.!?])\s+', text)
        
        # Capitalize first letter of each sentence
        for i in range(0, len(sentences), 2):
            if sentences[i]:
                sentences[i] = sentences[i][0].upper() + sentences[i][1:]
        
        # Join sentences
        return ''.join(sentences)