"""
Streamlit Audio Transcription App with OpenAI Whisper
Main application file
"""

import streamlit as st
import os
import time
from typing import Optional, Dict, Any
import tempfile

# Import our custom modules
from audio_processor import AudioProcessor
from whisper_client import WhisperClient
from transcription_utils import TranscriptionProcessor, TranscriptionExporter


# Page configuration
st.set_page_config(
    page_title="Audio Transcription App",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    .stat-item {
        text-align: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        margin: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'transcription_result' not in st.session_state:
        st.session_state.transcription_result = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'temp_files' not in st.session_state:
        st.session_state.temp_files = []


def get_api_key() -> Optional[str]:
    """Get OpenAI API key from secrets or environment"""
    # Try Streamlit secrets first
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key:
            return api_key
    except:
        pass
    
    # Try environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    return None


def display_header():
    """Display application header"""
    st.markdown('<h1 class="main-header">🎤 Audio Transcription App</h1>', unsafe_allow_html=True)
    
    # Check if audio processing is available
    try:
        from audio_processor import PYDUB_AVAILABLE
        if not PYDUB_AVAILABLE:
            st.error("⚠️ Audio Processing Not Available")
            st.error("The audio processing dependencies (pydub, pyaudioop-lts) are not installed.")
            st.error("Please install them using: pip install pydub pyaudioop-lts")
            return False
    except ImportError:
        st.error("⚠️ Audio Processing Module Not Found")
        st.error("The audio_processor module could not be imported. Please check your installation.")
        return False
    
    st.markdown("""
    <div class="info-box">
        <strong>Powered by OpenAI Whisper</strong><br>
        Upload audio files of any size and get accurate transcriptions with timestamps. 
        Large files are automatically split into chunks for optimal processing.
    </div>
    """, unsafe_allow_html=True)
    return True


def display_sidebar():
    """Display sidebar with settings and information"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key validation
        api_key = get_api_key()
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.error("❌ API Key not found")
            st.info("Please configure your OpenAI API key in the secrets or environment variables")
            return False
        
        # Language selection
        language = st.selectbox(
            "Language (optional)",
            ["Auto-detect", "English", "Spanish", "French", "German", "Italian", 
             "Portuguese", "Russian", "Japanese", "Korean", "Chinese"],
            help="Leave as 'Auto-detect' for automatic language detection"
        )
        
        # Convert language selection to code
        language_codes = {
            "Auto-detect": None,
            "English": "en",
            "Spanish": "es", 
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Japanese": "ja",
            "Korean": "ko",
            "Chinese": "zh"
        }
        selected_language = language_codes[language]
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            chunk_size = st.slider(
                "Chunk Size (MB)",
                min_value=10,
                max_value=24,
                value=24,
                help="Maximum size for each audio chunk"
            )
            
            overlap_seconds = st.slider(
                "Overlap (seconds)",
                min_value=1,
                max_value=5,
                value=3,
                help="Overlap between chunks to avoid word cutoffs"
            )
            
            show_timestamps = st.checkbox(
                "Show timestamps in output",
                value=True,
                help="Include timestamps in the transcription display"
            )
            
            force_time_based = st.checkbox(
                "Force time-based splitting",
                value=False,
                help="Skip silence detection and use time-based splitting (faster for large files)"
            )
        
        # App information
        st.markdown("---")
        st.markdown("### 📊 App Information")
        st.info("""
        **Supported Formats:** MP3, WAV, M4A, FLAC, OGG, WebM, MP4
        
        **File Size Limit:** 500MB
        
        **Processing:** Automatic chunking for large files
        
        **Output Formats:** TXT, SRT, VTT, JSON
        """)
        
        return {
            'api_key': api_key,
            'language': selected_language,
            'chunk_size': chunk_size,
            'overlap_seconds': overlap_seconds,
            'show_timestamps': show_timestamps,
            'force_time_based': force_time_based
        }


def display_file_upload():
    """Display file upload interface"""
    st.header("📁 Upload Audio File")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'webm', 'mp4', 'mpeg', 'mpga'],
        help="Supported formats: MP3, WAV, M4A, FLAC, OGG, WebM, MP4"
    )
    
    return uploaded_file


def display_audio_info(audio_processor: AudioProcessor, audio_segment):
    """Display audio file information"""
    info = audio_processor.get_audio_info(audio_segment)
    
    st.markdown("### 📋 File Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Duration", info['duration_formatted'])
    
    with col2:
        st.metric("Sample Rate", f"{info['sample_rate']} Hz")
    
    with col3:
        st.metric("Channels", info['channels'])
    
    with col4:
        st.metric("File Size", f"{info['file_size_mb']:.1f} MB")
    
    # Show chunking information
    needs_chunking = audio_processor.needs_chunking(audio_segment)
    if needs_chunking:
        st.info(f"📦 This file will be split into chunks (max {audio_processor.max_chunk_size_mb}MB each)")
    else:
        st.success("✅ File size is within limits - no chunking needed")


def process_transcription(uploaded_file, settings: Dict[str, Any]):
    """Process audio transcription with detailed debugging"""
    import time
    
    # Initialize components
    st.markdown("### 🔧 Initializing Components")
    init_start = time.time()
    
    audio_processor = AudioProcessor(
        max_chunk_size_mb=settings['chunk_size'],
        overlap_seconds=settings['overlap_seconds'],
        force_time_based=settings['force_time_based']
    )
    st.info(f"✅ Audio processor initialized (chunk size: {settings['chunk_size']}MB, overlap: {settings['overlap_seconds']}s)")
    
    whisper_client = WhisperClient(
        api_key=settings['api_key'],
        model="whisper-1"
    )
    st.info("✅ Whisper client initialized")
    
    transcription_processor = TranscriptionProcessor()
    exporter = TranscriptionExporter()
    st.info("✅ Transcription utilities initialized")
    
    init_time = time.time() - init_start
    st.success(f"🚀 All components ready in {init_time:.2f} seconds")
    
    # Validate and process audio file
    st.markdown("### 🔍 Validating Audio File")
    validation_start = time.time()
    
    st.info(f"📁 Processing file: {uploaded_file.name} ({uploaded_file.size / (1024*1024):.1f} MB)")
    
    is_valid, error_msg, audio_segment = audio_processor.validate_audio_file(uploaded_file)
    
    validation_time = time.time() - validation_start
    st.info(f"⏱️ Validation took {validation_time:.2f} seconds")
    
    if not is_valid:
        st.error(f"❌ {error_msg}")
        return None
    
    st.success("✅ Audio file validated successfully")
    
    # Display audio information
    display_audio_info(audio_processor, audio_segment)
    
    # Split audio into chunks
    st.markdown("### 🔄 Processing Audio")
    chunking_start = time.time()
    
    st.info("🔄 Starting intelligent audio chunking...")
    chunks = audio_processor.split_audio_intelligently(audio_segment)
    
    chunking_time = time.time() - chunking_start
    st.info(f"⏱️ Chunking took {chunking_time:.2f} seconds")
    st.success(f"📦 Audio split into {len(chunks)} chunks")
    
    # Show chunk details
    with st.expander("📊 Chunk Details", expanded=False):
        for i, (chunk, metadata) in enumerate(chunks):
            st.write(f"Chunk {i+1}: {metadata['duration']:.1f}s ({metadata.get('split_method', 'unknown')})")
    
    # Transcribe chunks
    st.markdown("### 🎯 Transcribing Audio")
    
    # Create progress bar and status
    progress_bar = st.progress(0)
    status_text = st.empty()
    time_text = st.empty()
    
    chunk_results = []
    transcription_start = time.time()
    
    for i, chunk_data in enumerate(chunks):
        chunk_start_time = time.time()
        status_text.text(f"🔄 Processing chunk {i + 1} of {len(chunks)}")
        
        # Show chunk info
        chunk, metadata = chunk_data
        st.info(f"📦 Chunk {i+1}: {metadata['duration']:.1f}s, method: {metadata.get('split_method', 'unknown')}")
        
        # Transcribe chunk
        result = whisper_client.transcribe_chunk(
            chunk_data, i, len(chunks), 
            language=settings['language']
        )
        
        chunk_time = time.time() - chunk_start_time
        time_text.text(f"⏱️ Chunk {i+1} completed in {chunk_time:.2f}s")
        
        # Show result
        if result['success']:
            st.success(f"✅ Chunk {i+1} transcribed: {len(result['text'])} characters")
        else:
            st.error(f"❌ Chunk {i+1} failed: {result.get('error', 'Unknown error')}")
        
        chunk_results.append(result)
        progress_bar.progress((i + 1) / len(chunks))
    
    transcription_time = time.time() - transcription_start
    st.info(f"⏱️ Total transcription time: {transcription_time:.2f} seconds")
    
    # Combine transcriptions
    st.markdown("### 🔗 Combining Results")
    combining_start = time.time()
    
    status_text.text("🔄 Combining transcriptions...")
    combined_result = transcription_processor.combine_transcriptions(chunk_results)
    
    combining_time = time.time() - combining_start
    st.info(f"⏱️ Combining took {combining_time:.2f} seconds")
    
    # Final status
    total_time = time.time() - init_start
    progress_bar.progress(1.0)
    status_text.text("✅ Transcription complete!")
    time_text.text(f"⏱️ Total processing time: {total_time:.2f} seconds")
    
    # Show processing summary
    with st.expander("📈 Processing Summary", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Time", f"{total_time:.1f}s")
        with col2:
            st.metric("Chunks Processed", len(chunks))
        with col3:
            successful_chunks = sum(1 for r in chunk_results if r['success'])
            st.metric("Success Rate", f"{successful_chunks}/{len(chunks)}")
        with col4:
            if combined_result['success']:
                st.metric("Final Text Length", f"{len(combined_result['text'])} chars")
            else:
                st.metric("Status", "Failed")
    
    return combined_result


def display_transcription_result(result: Dict[str, Any], settings: Dict[str, Any]):
    """Display transcription results"""
    if not result or not result.get('success', False):
        st.error("❌ Transcription failed")
        if result and result.get('error'):
            st.error(f"Error: {result['error']}")
        return
    
    st.markdown("### 📝 Transcription Results")
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Duration", f"{result['total_duration']:.1f}s")
    
    with col2:
        word_count = len(result['text'].split())
        st.metric("Word Count", word_count)
    
    with col3:
        st.metric("Chunks Processed", result['chunk_count'])
    
    with col4:
        if result.get('failed_chunks', 0) > 0:
            st.metric("Failed Chunks", result['failed_chunks'])
        else:
            st.metric("Success Rate", "100%")
    
    # Display transcription text
    st.markdown("### 📄 Transcription")
    
    # Format transcription
    formatted_text = result['text']
    if settings['show_timestamps'] and result.get('segments'):
        processor = TranscriptionProcessor()
        formatted_text = processor.format_transcription_with_timestamps(result, True)
    
    # Display in expandable text area
    with st.expander("View Full Transcription", expanded=True):
        st.text_area(
            "Transcription",
            value=formatted_text,
            height=400,
            disabled=True
        )
    
    # Export options
    st.markdown("### 💾 Export Options")
    
    exporter = TranscriptionExporter()
    base_filename = "transcription"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        txt_content = exporter.export_to_txt(result, settings['show_timestamps'])
        st.download_button(
            "📄 Download TXT",
            data=txt_content,
            file_name=exporter.get_export_filename(base_filename, "txt"),
            mime="text/plain"
        )
    
    with col2:
        srt_content = exporter.export_to_srt(result)
        st.download_button(
            "🎬 Download SRT",
            data=srt_content,
            file_name=exporter.get_export_filename(base_filename, "srt"),
            mime="text/plain"
        )
    
    with col3:
        vtt_content = exporter.export_to_vtt(result)
        st.download_button(
            "🌐 Download VTT",
            data=vtt_content,
            file_name=exporter.get_export_filename(base_filename, "vtt"),
            mime="text/vtt"
        )
    
    with col4:
        json_content = exporter.export_to_json(result)
        st.download_button(
            "📊 Download JSON",
            data=json_content,
            file_name=exporter.get_export_filename(base_filename, "json"),
            mime="application/json"
        )


def create_test_audio():
    """Create a small test audio file for debugging"""
    try:
        from pydub import AudioSegment
        import tempfile
        import os
        
        st.info("🎵 Creating test audio file...")
        
        # Create a 5-second test audio with some speech-like content
        # Generate a simple tone sequence
        test_audio = AudioSegment.silent(duration=1000)  # 1 second silence
        test_audio += AudioSegment.sine(440, duration=1000)  # 1 second tone
        test_audio += AudioSegment.silent(duration=1000)  # 1 second silence
        test_audio += AudioSegment.sine(880, duration=1000)  # 1 second higher tone
        test_audio += AudioSegment.silent(duration=1000)  # 1 second silence
        
        # Export to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        test_audio.export(temp_file.name, format='wav')
        
        st.success(f"✅ Test audio created: {temp_file.name}")
        st.info(f"📊 Test file info:")
        st.info(f"   - Duration: {len(test_audio) / 1000:.1f} seconds")
        st.info(f"   - Size: {os.path.getsize(temp_file.name) / 1024:.1f} KB")
        st.info(f"   - Format: WAV")
        
        # Clean up
        os.unlink(temp_file.name)
        
    except Exception as e:
        st.error(f"❌ Failed to create test audio: {str(e)}")

def test_api_connection(api_key: str):
    """Test OpenAI API connection"""
    try:
        from whisper_client import WhisperClient
        
        st.info("🔍 Testing OpenAI API connection...")
        
        client = WhisperClient(api_key=api_key, model="whisper-1")
        
        # Test API key validation
        is_valid = client.validate_api_key()
        
        if is_valid:
            st.success("✅ API key is valid and working")
            
            # Show cost estimation
            cost_info = client.estimate_cost(60)  # 1 minute
            st.info(f"💰 Cost estimation for 1 minute: ${cost_info['estimated_cost_usd']}")
            
        else:
            st.error("❌ API key validation failed")
            
    except Exception as e:
        st.error(f"❌ API connection test failed: {str(e)}")

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Display header and check dependencies
    if not display_header():
        st.stop()
    
    # Display sidebar and get settings
    settings = display_sidebar()
    if not settings:
        st.stop()
    
    # Display file upload
    uploaded_file = display_file_upload()
    
    # Debug section
    with st.expander("🔧 Debug Tools", expanded=False):
        st.markdown("**Test with a small audio file to debug processing:**")
        
        if st.button("🧪 Create Test Audio File"):
            create_test_audio()
        
        if st.button("🔍 Test API Connection"):
            test_api_connection(settings['api_key'])
    
    if uploaded_file is not None:
        # Process button
        if st.button("🚀 Start Transcription", type="primary"):
            with st.spinner("Processing your audio file..."):
                result = process_transcription(uploaded_file, settings)
                st.session_state.transcription_result = result
                st.session_state.processing_complete = True
        
        # Display results if processing is complete
        if st.session_state.processing_complete and st.session_state.transcription_result:
            display_transcription_result(st.session_state.transcription_result, settings)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Built with ❤️ using Streamlit and OpenAI Whisper</p>
        <p>For support or feedback, please contact the development team</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
