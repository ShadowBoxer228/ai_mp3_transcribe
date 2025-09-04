"""
OpenAI Whisper API Client for Streamlit Transcription App
Handles API communication, retry logic, and error handling
"""

import os
import time
import streamlit as st
from typing import Optional, Dict, Any, List
from openai import OpenAI
import tempfile


class WhisperClient:
    """Client for OpenAI Whisper API with retry logic and error handling"""
    
    def __init__(self, api_key: str, model: str = "whisper-1"):
        """
        Initialize Whisper client
        
        Args:
            api_key: OpenAI API key
            model: Whisper model to use (default: whisper-1)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def transcribe_audio_file(self, file_path: str, language: Optional[str] = None, 
                            prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file using OpenAI Whisper API with detailed debugging
        
        Args:
            file_path: Path to audio file
            language: Language code (optional, auto-detect if None)
            prompt: Optional prompt to guide transcription
            
        Returns:
            Dictionary with transcription results
        """
        import time
        
        for attempt in range(self.max_retries):
            try:
                st.info(f"🔄 API attempt {attempt + 1} of {self.max_retries}")
                
                with open(file_path, 'rb') as audio_file:
                    # Prepare transcription parameters
                    transcription_params = {
                        'model': self.model,
                        'file': audio_file,
                        'response_format': 'verbose_json',
                        'timestamp_granularities': ['word', 'segment']
                    }
                    
                    # Add optional parameters
                    if language:
                        transcription_params['language'] = language
                        st.info(f"🌍 Using specified language: {language}")
                    else:
                        st.info("🌍 Using auto-detect for language")
                    
                    if prompt:
                        transcription_params['prompt'] = prompt
                        st.info(f"💭 Using prompt: {prompt[:50]}...")
                    
                    st.info(f"📤 Sending request to OpenAI API...")
                    st.info(f"   - Model: {self.model}")
                    st.info(f"   - Response format: verbose_json")
                    st.info(f"   - Timestamp granularities: word, segment")
                    
                    # Make API call with timing
                    api_call_start = time.time()
                    response = self.client.audio.transcriptions.create(**transcription_params)
                    api_call_time = time.time() - api_call_start
                    
                    st.success(f"✅ API call successful in {api_call_time:.2f} seconds")
                    
                    # Extract response data
                    result = {
                        'success': True,
                        'text': response.text,
                        'language': getattr(response, 'language', language),
                        'duration': getattr(response, 'duration', None),
                        'segments': getattr(response, 'segments', []),
                        'words': getattr(response, 'words', []),
                        'error': None,
                        'api_call_time': api_call_time,
                        'attempt': attempt + 1
                    }
                    
                    # Show response details
                    st.info(f"📝 Response details:")
                    st.info(f"   - Text length: {len(result['text'])} characters")
                    st.info(f"   - Segments: {len(result['segments'])}")
                    st.info(f"   - Words: {len(result['words'])}")
                    if result['language']:
                        st.info(f"   - Detected language: {result['language']}")
                    if result['duration']:
                        st.info(f"   - Duration: {result['duration']:.2f}s")
                    
                    return result
                    
            except Exception as e:
                error_msg = str(e)
                st.warning(f"❌ Transcription attempt {attempt + 1} failed: {error_msg}")
                
                # Show detailed error information
                if "rate_limit" in error_msg.lower():
                    st.error("🚫 Rate limit exceeded - API is being throttled")
                elif "quota" in error_msg.lower():
                    st.error("💳 API quota exceeded - check your OpenAI account")
                elif "invalid" in error_msg.lower():
                    st.error("🔑 Invalid API key or request parameters")
                elif "timeout" in error_msg.lower():
                    st.error("⏰ Request timeout - network or server issue")
                else:
                    st.error(f"❓ Unknown error: {error_msg}")
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    st.info(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    return {
                        'success': False,
                        'text': '',
                        'language': language,
                        'duration': None,
                        'segments': [],
                        'words': [],
                        'error': error_msg,
                        'attempt': attempt + 1
                    }
        
        return {
            'success': False,
            'text': '',
            'language': language,
            'duration': None,
            'segments': [],
            'words': [],
            'error': 'Max retries exceeded'
        }
    
    def transcribe_chunk(self, chunk_data: tuple, chunk_index: int, 
                        total_chunks: int, language: Optional[str] = None,
                        prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe a single audio chunk with detailed debugging
        
        Args:
            chunk_data: Tuple of (audio_segment, metadata)
            chunk_index: Index of current chunk
            total_chunks: Total number of chunks
            language: Language code (optional)
            prompt: Optional prompt to guide transcription
            
        Returns:
            Dictionary with transcription results
        """
        import time
        
        audio_chunk, metadata = chunk_data
        
        st.info(f"🔧 Preparing chunk {chunk_index + 1} for transcription...")
        
        # Create temporary file for the chunk
        temp_file_start = time.time()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        
        st.info(f"📁 Exporting audio chunk to temporary file...")
        audio_chunk.export(temp_file.name, format='mp3', bitrate='128k')
        
        temp_file_time = time.time() - temp_file_start
        file_size = os.path.getsize(temp_file.name) / (1024 * 1024)  # MB
        st.info(f"✅ Temporary file created: {file_size:.2f}MB in {temp_file_time:.2f}s")
        
        try:
            # Update progress
            progress = (chunk_index + 1) / total_chunks
            st.progress(progress, text=f"Transcribing chunk {chunk_index + 1} of {total_chunks}")
            
            # Show API call details
            st.info(f"🌐 Making API call to OpenAI Whisper...")
            st.info(f"   - Model: {self.model}")
            st.info(f"   - Language: {language or 'auto-detect'}")
            st.info(f"   - File size: {file_size:.2f}MB")
            
            # Transcribe the chunk
            api_start = time.time()
            result = self.transcribe_audio_file(temp_file.name, language, prompt)
            api_time = time.time() - api_start
            
            st.info(f"⏱️ API call completed in {api_time:.2f} seconds")
            
            # Show API response details
            if result['success']:
                st.success(f"✅ API response received: {len(result['text'])} characters")
                if result.get('language'):
                    st.info(f"🌍 Detected language: {result['language']}")
                if result.get('duration'):
                    st.info(f"⏱️ Audio duration: {result['duration']:.2f}s")
            else:
                st.error(f"❌ API call failed: {result.get('error', 'Unknown error')}")
            
            # Add chunk metadata to result
            result['chunk_metadata'] = metadata
            result['chunk_index'] = chunk_index
            result['api_time'] = api_time
            result['file_size_mb'] = file_size
            
            return result
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
                st.info(f"🗑️ Temporary file cleaned up")
            except Exception as e:
                st.warning(f"Could not delete temporary file: {str(e)}")
    
    def transcribe_chunks_sequential(self, chunks: List[tuple], language: Optional[str] = None,
                                   prompt: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Transcribe multiple chunks sequentially
        
        Args:
            chunks: List of (audio_segment, metadata) tuples
            language: Language code (optional)
            prompt: Optional prompt to guide transcription
            
        Returns:
            List of transcription results
        """
        results = []
        total_chunks = len(chunks)
        
        st.info(f"Starting transcription of {total_chunks} chunks...")
        
        for i, chunk_data in enumerate(chunks):
            result = self.transcribe_chunk(chunk_data, i, total_chunks, language, prompt)
            results.append(result)
            
            # Show intermediate progress
            if result['success']:
                st.success(f"✅ Chunk {i + 1} transcribed successfully")
            else:
                st.error(f"❌ Chunk {i + 1} failed: {result['error']}")
        
        return results
    
    def validate_api_key(self) -> bool:
        """
        Validate OpenAI API key by making a test request
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Create a short silent audio file for testing
            from pydub import AudioSegment
            test_audio = AudioSegment.silent(duration=1000)  # 1 second of silence
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            test_audio.export(temp_file.name, format='mp3')
            
            try:
                # Try to transcribe the silent audio
                result = self.transcribe_audio_file(temp_file.name)
                return result['success'] or 'quota' not in result.get('error', '').lower()
            finally:
                os.unlink(temp_file.name)
                
        except Exception as e:
            error_msg = str(e).lower()
            # Check for common API key errors
            if any(keyword in error_msg for keyword in ['invalid', 'unauthorized', 'forbidden']):
                return False
            # Other errors might be network-related, so we'll assume the key is valid
            return True
    
    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get API usage information (if available)
        
        Returns:
            Dictionary with usage information
        """
        try:
            # Note: OpenAI doesn't provide real-time usage info in the API
            # This is a placeholder for future implementation
            return {
                'available': False,
                'message': 'Usage information not available in current API version'
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def estimate_cost(self, duration_seconds: float) -> Dict[str, Any]:
        """
        Estimate transcription cost based on duration
        
        Args:
            duration_seconds: Audio duration in seconds
            
        Returns:
            Dictionary with cost estimation
        """
        # Whisper API pricing (as of 2024): $0.006 per minute
        cost_per_minute = 0.006
        duration_minutes = duration_seconds / 60.0
        estimated_cost = duration_minutes * cost_per_minute
        
        return {
            'duration_seconds': duration_seconds,
            'duration_minutes': duration_minutes,
            'cost_per_minute': cost_per_minute,
            'estimated_cost_usd': round(estimated_cost, 4),
            'note': 'Cost estimation based on current OpenAI pricing'
        }
