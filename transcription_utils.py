"""
Transcription Utilities for Streamlit Transcription App
Handles text processing, formatting, and export functionality
"""

import re
import json
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import timedelta


class TranscriptionProcessor:
    """Handles transcription processing, formatting, and export"""
    
    def __init__(self):
        self.overlap_threshold = 2.0  # seconds
    
    def combine_transcriptions(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine multiple chunk transcriptions into a single result
        
        Args:
            chunk_results: List of transcription results from chunks
            
        Returns:
            Combined transcription result
        """
        if not chunk_results:
            return {
                'text': '',
                'segments': [],
                'words': [],
                'language': None,
                'total_duration': 0,
                'chunk_count': 0,
                'success': False
            }
        
        # Filter successful results
        successful_results = [r for r in chunk_results if r.get('success', False)]
        
        if not successful_results:
            return {
                'text': '',
                'segments': [],
                'words': [],
                'language': None,
                'total_duration': 0,
                'chunk_count': len(chunk_results),
                'success': False,
                'error': 'No successful transcriptions'
            }
        
        # Combine text
        combined_text = self._combine_text(successful_results)
        
        # Combine segments with proper timing
        combined_segments = self._combine_segments(successful_results)
        
        # Combine words with proper timing
        combined_words = self._combine_words(successful_results)
        
        # Get language (should be consistent across chunks)
        language = successful_results[0].get('language')
        
        # Calculate total duration
        total_duration = max(
            (r.get('chunk_metadata', {}).get('end_time', 0) for r in successful_results),
            default=0
        )
        
        return {
            'text': combined_text,
            'segments': combined_segments,
            'words': combined_words,
            'language': language,
            'total_duration': total_duration,
            'chunk_count': len(successful_results),
            'success': True,
            'failed_chunks': len(chunk_results) - len(successful_results)
        }
    
    def _combine_text(self, results: List[Dict[str, Any]]) -> str:
        """Combine text from multiple chunks, handling overlaps"""
        if not results:
            return ""
        
        # Sort by chunk index
        sorted_results = sorted(results, key=lambda x: x.get('chunk_index', 0))
        
        combined_parts = []
        for i, result in enumerate(sorted_results):
            text = result.get('text', '').strip()
            if not text:
                continue
            
            # For first chunk, add all text
            if i == 0:
                combined_parts.append(text)
            else:
                # For subsequent chunks, try to remove overlap
                overlap_removed = self._remove_text_overlap(combined_parts[-1], text)
                combined_parts.append(overlap_removed)
        
        return ' '.join(combined_parts)
    
    def _remove_text_overlap(self, previous_text: str, current_text: str) -> str:
        """Remove overlapping text between chunks"""
        if not previous_text or not current_text:
            return current_text
        
        # Simple overlap detection based on word matching
        prev_words = previous_text.split()
        curr_words = current_text.split()
        
        # Find overlap by matching end of previous with start of current
        max_overlap = min(len(prev_words), len(curr_words), 10)  # Max 10 words overlap
        
        for overlap_len in range(max_overlap, 0, -1):
            if prev_words[-overlap_len:] == curr_words[:overlap_len]:
                return ' '.join(curr_words[overlap_len:])
        
        return current_text
    
    def _combine_segments(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine segments from multiple chunks with proper timing"""
        combined_segments = []
        
        # Sort by chunk index
        sorted_results = sorted(results, key=lambda x: x.get('chunk_index', 0))
        
        for result in sorted_results:
            segments = result.get('segments', [])
            chunk_metadata = result.get('chunk_metadata', {})
            chunk_start_time = chunk_metadata.get('start_time', 0)
            
            for segment in segments:
                # Handle both dictionary and Pydantic object formats
                if hasattr(segment, 'start'):
                    # Pydantic object - convert to dictionary
                    adjusted_segment = {
                        'start': getattr(segment, 'start', 0) + chunk_start_time,
                        'end': getattr(segment, 'end', 0) + chunk_start_time,
                        'text': getattr(segment, 'text', ''),
                        'id': getattr(segment, 'id', None),
                        'seek': getattr(segment, 'seek', None),
                        'tokens': getattr(segment, 'tokens', []),
                        'temperature': getattr(segment, 'temperature', None),
                        'avg_logprob': getattr(segment, 'avg_logprob', None),
                        'compression_ratio': getattr(segment, 'compression_ratio', None),
                        'no_speech_prob': getattr(segment, 'no_speech_prob', None)
                    }
                else:
                    # Dictionary
                    adjusted_segment = segment.copy()
                    if 'start' in segment:
                        adjusted_segment['start'] += chunk_start_time
                    if 'end' in segment:
                        adjusted_segment['end'] += chunk_start_time
                
                combined_segments.append(adjusted_segment)
        
        return combined_segments
    
    def _combine_words(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine words from multiple chunks with proper timing"""
        combined_words = []
        
        # Sort by chunk index
        sorted_results = sorted(results, key=lambda x: x.get('chunk_index', 0))
        
        for result in sorted_results:
            words = result.get('words', [])
            chunk_metadata = result.get('chunk_metadata', {})
            chunk_start_time = chunk_metadata.get('start_time', 0)
            
            for word in words:
                # Handle both dictionary and Pydantic object formats
                if hasattr(word, 'start'):
                    # Pydantic object - convert to dictionary
                    adjusted_word = {
                        'start': getattr(word, 'start', 0) + chunk_start_time,
                        'end': getattr(word, 'end', 0) + chunk_start_time,
                        'word': getattr(word, 'word', ''),
                        'probability': getattr(word, 'probability', None)
                    }
                else:
                    # Dictionary
                    adjusted_word = word.copy()
                    if 'start' in word:
                        adjusted_word['start'] += chunk_start_time
                    if 'end' in word:
                        adjusted_word['end'] += chunk_start_time
                
                combined_words.append(adjusted_word)
        
        return combined_words
    
    def format_transcription_with_timestamps(self, transcription: Dict[str, Any], 
                                           show_timestamps: bool = True) -> str:
        """
        Format transcription with timestamps
        
        Args:
            transcription: Transcription result dictionary
            show_timestamps: Whether to include timestamps
            
        Returns:
            Formatted transcription text
        """
        if not transcription.get('success', False):
            return "Transcription failed."
        
        if show_timestamps and transcription.get('segments'):
            return self._format_with_segment_timestamps(transcription)
        else:
            return transcription.get('text', '')
    
    def _format_with_segment_timestamps(self, transcription: Dict[str, Any]) -> str:
        """Format transcription with segment timestamps"""
        segments = transcription.get('segments', [])
        if not segments:
            return transcription.get('text', '')
        
        formatted_lines = []
        for segment in segments:
            # Handle both dictionary and Pydantic object formats
            if hasattr(segment, 'start'):
                # Pydantic object
                start_time = self._format_timestamp(getattr(segment, 'start', 0))
                end_time = self._format_timestamp(getattr(segment, 'end', 0))
                text = getattr(segment, 'text', '').strip()
            else:
                # Dictionary
                start_time = self._format_timestamp(segment.get('start', 0))
                end_time = self._format_timestamp(segment.get('end', 0))
                text = segment.get('text', '').strip()
            
            if text:
                formatted_lines.append(f"[{start_time} - {end_time}] {text}")
        
        return '\n'.join(formatted_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to HH:MM:SS.mmm format"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{seconds:06.3f}"


class TranscriptionExporter:
    """Handles export of transcriptions to various formats"""
    
    def __init__(self):
        self.processor = TranscriptionProcessor()
    
    def export_to_txt(self, transcription: Dict[str, Any], include_timestamps: bool = False) -> str:
        """
        Export transcription to plain text format
        
        Args:
            transcription: Transcription result dictionary
            include_timestamps: Whether to include timestamps
            
        Returns:
            Plain text content
        """
        if include_timestamps:
            return self.processor.format_transcription_with_timestamps(transcription, True)
        else:
            return transcription.get('text', '')
    
    def export_to_srt(self, transcription: Dict[str, Any]) -> str:
        """
        Export transcription to SRT subtitle format
        
        Args:
            transcription: Transcription result dictionary
            
        Returns:
            SRT format content
        """
        segments = transcription.get('segments', [])
        if not segments:
            return ""
        
        srt_lines = []
        for i, segment in enumerate(segments, 1):
            # Handle both dictionary and Pydantic object formats
            if hasattr(segment, 'start'):
                # Pydantic object
                start_time = self._format_srt_timestamp(getattr(segment, 'start', 0))
                end_time = self._format_srt_timestamp(getattr(segment, 'end', 0))
                text = getattr(segment, 'text', '').strip()
            else:
                # Dictionary
                start_time = self._format_srt_timestamp(segment.get('start', 0))
                end_time = self._format_srt_timestamp(segment.get('end', 0))
                text = segment.get('text', '').strip()
            
            if text:
                srt_lines.append(f"{i}")
                srt_lines.append(f"{start_time} --> {end_time}")
                srt_lines.append(text)
                srt_lines.append("")  # Empty line between subtitles
        
        return '\n'.join(srt_lines)
    
    def export_to_vtt(self, transcription: Dict[str, Any]) -> str:
        """
        Export transcription to WebVTT format
        
        Args:
            transcription: Transcription result dictionary
            
        Returns:
            VTT format content
        """
        segments = transcription.get('segments', [])
        if not segments:
            return ""
        
        vtt_lines = ["WEBVTT", ""]
        
        for segment in segments:
            # Handle both dictionary and Pydantic object formats
            if hasattr(segment, 'start'):
                # Pydantic object
                start_time = self._format_vtt_timestamp(getattr(segment, 'start', 0))
                end_time = self._format_vtt_timestamp(getattr(segment, 'end', 0))
                text = getattr(segment, 'text', '').strip()
            else:
                # Dictionary
                start_time = self._format_vtt_timestamp(segment.get('start', 0))
                end_time = self._format_vtt_timestamp(segment.get('end', 0))
                text = segment.get('text', '').strip()
            
            if text:
                vtt_lines.append(f"{start_time} --> {end_time}")
                vtt_lines.append(text)
                vtt_lines.append("")  # Empty line between cues
        
        return '\n'.join(vtt_lines)
    
    def export_to_json(self, transcription: Dict[str, Any]) -> str:
        """
        Export transcription to JSON format
        
        Args:
            transcription: Transcription result dictionary
            
        Returns:
            JSON format content
        """
        export_data = {
            'text': transcription.get('text', ''),
            'language': transcription.get('language'),
            'duration': transcription.get('total_duration', 0),
            'segments': transcription.get('segments', []),
            'words': transcription.get('words', []),
            'metadata': {
                'chunk_count': transcription.get('chunk_count', 0),
                'failed_chunks': transcription.get('failed_chunks', 0),
                'export_timestamp': self._get_current_timestamp()
            }
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """Format timestamp for SRT format (HH:MM:SS,mmm)"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def _format_vtt_timestamp(self, seconds: float) -> str:
        """Format timestamp for VTT format (HH:MM:SS.mmm)"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{seconds:06.3f}"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_export_filename(self, base_name: str, format_type: str) -> str:
        """
        Generate export filename
        
        Args:
            base_name: Base filename without extension
            format_type: Export format (txt, srt, vtt, json)
            
        Returns:
            Complete filename
        """
        # Clean base name
        clean_name = re.sub(r'[^\w\-_\.]', '_', base_name)
        clean_name = clean_name.replace(' ', '_')
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{clean_name}_{timestamp}.{format_type}"
