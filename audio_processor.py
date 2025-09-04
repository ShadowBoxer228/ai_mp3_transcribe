"""
Audio Processing Module for Streamlit Transcription App
Handles audio file validation, chunking, and format conversion
"""

import os
import tempfile
import io
from typing import List, Tuple, Optional
import streamlit as st

# Try to import pydub with fallback handling
try:
    from pydub import AudioSegment
    from pydub.silence import split_on_silence, detect_silence
    PYDUB_AVAILABLE = True
except ImportError as e:
    # Don't use st.error here as it might cause issues during import
    print(f"Warning: pydub import failed: {str(e)}")
    print("Please install required dependencies: pip install pydub pyaudioop-lts")
    PYDUB_AVAILABLE = False
    # Create dummy classes for graceful degradation
    class AudioSegment:
        pass
    def split_on_silence(*args, **kwargs):
        return []
    def detect_silence(*args, **kwargs):
        return []


class AudioProcessor:
    """Handles audio file processing, validation, and intelligent chunking"""
    
    # Supported audio formats
    SUPPORTED_FORMATS = {
        'mp3': 'mp3',
        'wav': 'wav', 
        'm4a': 'mp4',
        'flac': 'flac',
        'ogg': 'ogg',
        'webm': 'webm',
        'mp4': 'mp4',
        'mpeg': 'mp3',
        'mpga': 'mp3'
    }
    
    def __init__(self, max_chunk_size_mb: int = 24, overlap_seconds: int = 3, force_time_based: bool = False):
        self.max_chunk_size_mb = max_chunk_size_mb
        self.overlap_seconds = overlap_seconds
        self.max_chunk_size_bytes = max_chunk_size_mb * 1024 * 1024
        self.force_time_based = force_time_based
    
    def validate_audio_file(self, uploaded_file) -> Tuple[bool, str, Optional[AudioSegment]]:
        """
        Validate uploaded audio file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message, audio_segment)
        """
        if not PYDUB_AVAILABLE:
            return False, "Audio processing dependencies not available. Please install pydub and pyaudioop-lts.", None
            
        try:
            # Check file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in self.SUPPORTED_FORMATS:
                return False, f"Unsupported file format: {file_extension}. Supported formats: {', '.join(self.SUPPORTED_FORMATS.keys())}", None
            
            # Check file size (basic check)
            if uploaded_file.size > 500 * 1024 * 1024:  # 500MB limit
                return False, "File too large. Maximum size is 500MB.", None
            
            # Load audio file
            audio_data = uploaded_file.read()
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format=file_extension)
            
            # Check if audio is too short
            if len(audio_segment) < 1000:  # Less than 1 second
                return False, "Audio file is too short (less than 1 second).", None
            
            return True, "", audio_segment
            
        except Exception as e:
            return False, f"Error loading audio file: {str(e)}", None
    
    def get_audio_info(self, audio_segment: AudioSegment) -> dict:
        """
        Get audio file information
        
        Args:
            audio_segment: AudioSegment object
            
        Returns:
            Dictionary with audio information
        """
        duration_seconds = len(audio_segment) / 1000.0
        sample_rate = audio_segment.frame_rate
        channels = audio_segment.channels
        bit_depth = audio_segment.sample_width * 8
        
        return {
            'duration_seconds': duration_seconds,
            'duration_formatted': self._format_duration(duration_seconds),
            'sample_rate': sample_rate,
            'channels': channels,
            'bit_depth': bit_depth,
            'file_size_mb': len(audio_segment.raw_data) / (1024 * 1024)
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def needs_chunking(self, audio_segment: AudioSegment) -> bool:
        """
        Check if audio file needs to be chunked
        
        Args:
            audio_segment: AudioSegment object
            
        Returns:
            True if chunking is needed
        """
        # Estimate file size when exported as MP3
        estimated_size = len(audio_segment.raw_data) / (1024 * 1024)
        return estimated_size > self.max_chunk_size_mb
    
    def split_audio_intelligently(self, audio_segment: AudioSegment) -> List[Tuple[AudioSegment, dict]]:
        """
        Split audio file into chunks using intelligent segmentation with debugging
        
        Args:
            audio_segment: AudioSegment object to split
            
        Returns:
            List of tuples (audio_chunk, metadata)
        """
        import time
        
        st.info("🔍 Analyzing audio file for chunking...")
        
        chunks = []
        
        if not self.needs_chunking(audio_segment):
            # File is small enough, return as single chunk
            st.info("✅ File is small enough - no chunking needed")
            metadata = {
                'chunk_index': 0,
                'start_time': 0,
                'end_time': len(audio_segment) / 1000.0,
                'duration': len(audio_segment) / 1000.0,
                'is_single_chunk': True,
                'split_method': 'single_chunk'
            }
            return [(audio_segment, metadata)]
        
        # Calculate target chunk duration based on file size
        total_duration = len(audio_segment) / 1000.0
        estimated_chunks = max(1, int(len(audio_segment.raw_data) / self.max_chunk_size_bytes) + 1)
        target_chunk_duration = total_duration / estimated_chunks
        
        st.info(f"📊 Chunking analysis:")
        st.info(f"   - Total duration: {total_duration:.1f} seconds")
        st.info(f"   - Estimated chunks needed: {estimated_chunks}")
        st.info(f"   - Target chunk duration: {target_chunk_duration:.1f} seconds")
        st.info(f"   - Max chunk size: {self.max_chunk_size_mb}MB")
        
        # Decide whether to attempt silence-based splitting
        should_try_silence = not self.force_time_based and total_duration < 600  # Only try silence detection for files < 10 minutes
        
        if should_try_silence:
            st.info("🔇 Attempting silence-based splitting...")
            silence_start = time.time()
            silence_chunks = self._split_on_silence(audio_segment, target_chunk_duration)
            silence_time = time.time() - silence_start
            
            if silence_chunks:
                st.success(f"✅ Silence-based splitting successful: {len(silence_chunks)} chunks in {silence_time:.2f}s")
                chunks = silence_chunks
            else:
                st.warning(f"⚠️ Silence-based splitting failed, using time-based splitting")
                # Fallback to time-based splitting
                time_start = time.time()
                chunks = self._split_by_time(audio_segment, target_chunk_duration)
                time_time = time.time() - time_start
                st.info(f"✅ Time-based splitting completed: {len(chunks)} chunks in {time_time:.2f}s")
        else:
            if self.force_time_based:
                st.info("⏭️ Force time-based splitting enabled - skipping silence detection")
            else:
                st.info(f"⏭️ Skipping silence detection for large file ({total_duration:.1f}s) - using time-based splitting")
            # Use time-based splitting directly for large files
            time_start = time.time()
            chunks = self._split_by_time(audio_segment, target_chunk_duration)
            time_time = time.time() - time_start
            st.info(f"✅ Time-based splitting completed: {len(chunks)} chunks in {time_time:.2f}s")
        
        # Add overlap between chunks
        st.info(f"🔗 Adding {self.overlap_seconds}s overlap between chunks...")
        overlap_start = time.time()
        chunks_with_overlap = self._add_overlap_to_chunks(chunks)
        overlap_time = time.time() - overlap_start
        
        st.success(f"✅ Overlap processing completed in {overlap_time:.2f}s")
        st.info(f"📦 Final result: {len(chunks_with_overlap)} chunks ready for transcription")
        
        return chunks_with_overlap
    
    def _split_on_silence(self, audio_segment: AudioSegment, target_duration: float) -> List[Tuple[AudioSegment, dict]]:
        """
        Split audio on silence with target duration consideration and timeout
        
        Args:
            audio_segment: AudioSegment object
            target_duration: Target duration for each chunk in seconds
            
        Returns:
            List of audio chunks with metadata
        """
        import signal
        import time
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Silence detection timed out")
        
        try:
            # Set a timeout for silence detection (30 seconds max)
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            st.info("🔇 Analyzing audio for silence patterns...")
            
            # For large files, use a more aggressive approach
            total_duration = len(audio_segment) / 1000.0
            if total_duration > 300:  # More than 5 minutes
                st.info("📊 Large file detected - using optimized silence detection")
                # Use higher threshold and longer minimum silence for large files
                silence_thresh = audio_segment.dBFS - 20  # 20dB below average volume
                min_silence_len = 2000  # 2 seconds minimum silence
            else:
                # Standard settings for smaller files
                silence_thresh = audio_segment.dBFS - 16  # 16dB below average volume
                min_silence_len = 1000  # 1 second minimum silence
            
            st.info(f"   - Silence threshold: {silence_thresh:.1f} dB")
            st.info(f"   - Minimum silence length: {min_silence_len}ms")
            
            # Split on silence
            chunks = split_on_silence(
                audio_segment,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh,
                keep_silence=500  # Keep 0.5 seconds of silence
            )
            
            signal.alarm(0)  # Cancel the alarm
            
            if not chunks:
                st.warning("⚠️ No silence patterns found - will use time-based splitting")
                return []
            
            st.info(f"✅ Found {len(chunks)} silence-based chunks")
            
            # If chunks are too large, split them further
            final_chunks = []
            chunk_index = 0
            current_time = 0
            
            for chunk in chunks:
                chunk_duration = len(chunk) / 1000.0
                
                if chunk_duration <= target_duration * 1.5:  # Within reasonable range
                    metadata = {
                        'chunk_index': chunk_index,
                        'start_time': current_time,
                        'end_time': current_time + chunk_duration,
                        'duration': chunk_duration,
                        'split_method': 'silence'
                    }
                    final_chunks.append((chunk, metadata))
                    current_time += chunk_duration
                    chunk_index += 1
                else:
                    # Split large chunk by time
                    st.info(f"📦 Chunk {chunk_index + 1} too large ({chunk_duration:.1f}s) - splitting by time")
                    time_chunks = self._split_by_time(chunk, target_duration)
                    for time_chunk, time_metadata in time_chunks:
                        time_metadata['chunk_index'] = chunk_index
                        time_metadata['start_time'] = current_time
                        time_metadata['end_time'] = current_time + time_metadata['duration']
                        time_metadata['split_method'] = 'time_fallback'
                        final_chunks.append((time_chunk, time_metadata))
                        current_time += time_metadata['duration']
                        chunk_index += 1
            
            return final_chunks
            
        except TimeoutError:
            signal.alarm(0)  # Cancel the alarm
            st.warning("⏰ Silence detection timed out after 30 seconds - using time-based splitting")
            return []
        except Exception as e:
            signal.alarm(0)  # Cancel the alarm
            st.warning(f"❌ Silence detection failed: {str(e)}. Using time-based splitting.")
            return []
    
    def _split_by_time(self, audio_segment: AudioSegment, target_duration: float) -> List[Tuple[AudioSegment, dict]]:
        """
        Split audio by time intervals
        
        Args:
            audio_segment: AudioSegment object
            target_duration: Target duration for each chunk in seconds
            
        Returns:
            List of audio chunks with metadata
        """
        chunks = []
        total_duration = len(audio_segment) / 1000.0
        chunk_index = 0
        
        start_time = 0
        while start_time < total_duration:
            end_time = min(start_time + target_duration, total_duration)
            
            # Convert to milliseconds
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000)
            
            chunk = audio_segment[start_ms:end_ms]
            duration = len(chunk) / 1000.0
            
            metadata = {
                'chunk_index': chunk_index,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'split_method': 'time'
            }
            
            chunks.append((chunk, metadata))
            start_time = end_time
            chunk_index += 1
        
        return chunks
    
    def _add_overlap_to_chunks(self, chunks: List[Tuple[AudioSegment, dict]]) -> List[Tuple[AudioSegment, dict]]:
        """
        Add overlap between chunks to avoid word cutoffs
        
        Args:
            chunks: List of audio chunks with metadata
            
        Returns:
            List of chunks with overlap added
        """
        if len(chunks) <= 1:
            return chunks
        
        overlap_ms = self.overlap_seconds * 1000
        final_chunks = []
        
        for i, (chunk, metadata) in enumerate(chunks):
            if i == 0:
                # First chunk: add overlap at the end
                if len(chunks) > 1:
                    overlap_duration = min(overlap_ms, len(chunk) // 4)  # Max 25% of chunk
                    extended_chunk = chunk + AudioSegment.silent(duration=overlap_duration)
                    metadata['end_time'] += overlap_duration / 1000.0
                    metadata['duration'] = len(extended_chunk) / 1000.0
                    final_chunks.append((extended_chunk, metadata))
                else:
                    final_chunks.append((chunk, metadata))
            elif i == len(chunks) - 1:
                # Last chunk: add overlap at the beginning
                overlap_duration = min(overlap_ms, len(chunk) // 4)
                extended_chunk = AudioSegment.silent(duration=overlap_duration) + chunk
                metadata['start_time'] -= overlap_duration / 1000.0
                metadata['duration'] = len(extended_chunk) / 1000.0
                final_chunks.append((extended_chunk, metadata))
            else:
                # Middle chunks: add overlap at both ends
                overlap_duration = min(overlap_ms, len(chunk) // 4)
                extended_chunk = AudioSegment.silent(duration=overlap_duration) + chunk + AudioSegment.silent(duration=overlap_duration)
                metadata['start_time'] -= overlap_duration / 1000.0
                metadata['end_time'] += overlap_duration / 1000.0
                metadata['duration'] = len(extended_chunk) / 1000.0
                final_chunks.append((extended_chunk, metadata))
        
        return final_chunks
    
    def export_chunk_to_temp_file(self, chunk: AudioSegment, chunk_index: int) -> str:
        """
        Export audio chunk to temporary file
        
        Args:
            chunk: AudioSegment object
            chunk_index: Index of the chunk
            
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        chunk.export(temp_file.name, format='mp3', bitrate='128k')
        return temp_file.name
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """
        Clean up temporary files
        
        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                st.warning(f"Could not delete temporary file {file_path}: {str(e)}")
