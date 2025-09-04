"""
Streamlit Audio Transcription App - Cloud Optimized Version
Optimized for Streamlit Cloud deployment with enhanced debugging
"""

import streamlit as st
import os
import time
import tempfile
import traceback
from typing import Optional, Dict, Any

# Import our custom modules
try:
    from audio_processor import AudioProcessor
    from whisper_client import WhisperClient
    from transcription_utils import TranscriptionProcessor, TranscriptionExporter
    st.success("✅ All modules imported successfully")
except ImportError as e:
    st.error(f"❌ Import error: {str(e)}")
    st.stop()

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
    .debug-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def log_debug(message: str, level: str = "INFO"):
    """Enhanced logging for cloud debugging"""
    timestamp = time.strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="debug-box">
        <strong>[{timestamp}] {level}:</strong> {message}
    </div>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables with cloud debugging"""
    log_debug("Initializing session state")
    
    if 'transcription_result' not in st.session_state:
        st.session_state.transcription_result = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'temp_files' not in st.session_state:
        st.session_state.temp_files = []
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = True
    
    log_debug("Session state initialized successfully")


def get_api_key() -> Optional[str]:
    """Get OpenAI API key with cloud debugging"""
    log_debug("Attempting to get API key")
    
    # Try Streamlit secrets first (for cloud deployment)
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key:
            log_debug("✅ API key found in Streamlit secrets")
            return api_key
    except Exception as e:
        log_debug(f"⚠️ Streamlit secrets error: {str(e)}", "WARNING")
    
    # Try environment variable (for local development)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        log_debug("✅ API key found in environment variables")
        return api_key
    
    log_debug("❌ No API key found", "ERROR")
    return None


def display_header():
    """Display application header with cloud info"""
    st.markdown('<h1 class="main-header">🎤 Audio Transcription App</h1>', unsafe_allow_html=True)
    
    # Show deployment info
    deployment_info = "🌐 **Cloud Deployment**" if os.getenv("STREAMLIT_CLOUD") else "💻 **Local Development**"
    st.markdown(f"""
    <div class="info-box">
        <strong>Powered by OpenAI Whisper</strong><br>
        {deployment_info}<br>
        Upload audio files of any size and get accurate transcriptions with timestamps. 
        Large files are automatically split into chunks for optimal processing.
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display sidebar with settings and cloud debugging"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key validation with cloud debugging
        api_key = get_api_key()
        if api_key:
            st.success("✅ API Key configured")
            log_debug("API key validation successful")
        else:
            st.error("❌ API Key not found")
            log_debug("API key validation failed", "ERROR")
            return False
        
        # Debug mode toggle
        debug_mode = st.checkbox("🐛 Debug Mode", value=st.session_state.debug_mode)
        st.session_state.debug_mode = debug_mode
        
        if debug_mode:
            st.markdown("### 🔍 Debug Information")
            st.info(f"**Environment:** {'Cloud' if os.getenv('STREAMLIT_CLOUD') else 'Local'}")
            st.info(f"**Python Version:** {os.sys.version}")
            st.info(f"**Working Directory:** {os.getcwd()}")
        
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
            'force_time_based': force_time_based,
            'debug_mode': debug_mode
        }


def display_file_upload():
    """Display file upload interface with cloud debugging"""
    st.header("📁 Upload Audio File")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'webm', 'mp4', 'mpeg', 'mpga'],
        help="Supported formats: MP3, WAV, M4A, FLAC, OGG, WebM, MP4"
    )
    
    if uploaded_file:
        log_debug(f"File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
    
    return uploaded_file


def process_transcription(uploaded_file, settings: Dict[str, Any]):
    """Process audio transcription with comprehensive cloud debugging"""
    log_debug("Starting transcription process")
    
    try:
        # Initialize components
        st.markdown("### 🔧 Initializing Components")
        init_start = time.time()
        
        log_debug("Creating AudioProcessor")
        audio_processor = AudioProcessor(
            max_chunk_size_mb=settings['chunk_size'],
            overlap_seconds=settings['overlap_seconds'],
            force_time_based=settings['force_time_based']
        )
        st.info(f"✅ Audio processor initialized (chunk size: {settings['chunk_size']}MB, overlap: {settings['overlap_seconds']}s)")
        
        log_debug("Creating WhisperClient")
        whisper_client = WhisperClient(
            api_key=settings['api_key'],
            model="whisper-1"
        )
        st.info("✅ Whisper client initialized")
        
        log_debug("Creating TranscriptionProcessor and Exporter")
        transcription_processor = TranscriptionProcessor()
        exporter = TranscriptionExporter()
        st.info("✅ Transcription utilities initialized")
        
        init_time = time.time() - init_start
        st.success(f"🚀 All components ready in {init_time:.2f} seconds")
        log_debug(f"Component initialization completed in {init_time:.2f}s")
        
        # Validate and process audio file
        st.markdown("### 🔍 Validating Audio File")
        validation_start = time.time()
        
        st.info(f"📁 Processing file: {uploaded_file.name} ({uploaded_file.size / (1024*1024):.1f} MB)")
        log_debug(f"Validating file: {uploaded_file.name}")
        
        is_valid, error_msg, audio_segment = audio_processor.validate_audio_file(uploaded_file)
        
        validation_time = time.time() - validation_start
        st.info(f"⏱️ Validation took {validation_time:.2f} seconds")
        log_debug(f"File validation completed in {validation_time:.2f}s")
        
        if not is_valid:
            st.error(f"❌ {error_msg}")
            log_debug(f"File validation failed: {error_msg}", "ERROR")
            return None
        
        st.success("✅ Audio file validated successfully")
        log_debug("File validation successful")
        
        # Split audio into chunks
        st.markdown("### 🔄 Processing Audio")
        chunking_start = time.time()
        
        st.info("🔄 Starting intelligent audio chunking...")
        log_debug("Starting audio chunking process")
        
        chunks = audio_processor.split_audio_intelligently(audio_segment)
        
        chunking_time = time.time() - chunking_start
        st.info(f"⏱️ Chunking took {chunking_time:.2f} seconds")
        st.success(f"📦 Audio split into {len(chunks)} chunks")
        log_debug(f"Audio chunking completed: {len(chunks)} chunks in {chunking_time:.2f}s")
        
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
            log_debug(f"Processing chunk {i+1}: {metadata['duration']:.1f}s")
            
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
                log_debug(f"Chunk {i+1} transcribed successfully: {len(result['text'])} chars")
            else:
                st.error(f"❌ Chunk {i+1} failed: {result.get('error', 'Unknown error')}")
                log_debug(f"Chunk {i+1} failed: {result.get('error', 'Unknown error')}", "ERROR")
            
            chunk_results.append(result)
            progress_bar.progress((i + 1) / len(chunks))
        
        transcription_time = time.time() - transcription_start
        st.info(f"⏱️ Total transcription time: {transcription_time:.2f} seconds")
        log_debug(f"Transcription completed in {transcription_time:.2f}s")
        
        # Combine transcriptions
        st.markdown("### 🔗 Combining Results")
        combining_start = time.time()
        
        status_text.text("🔄 Combining transcriptions...")
        log_debug("Combining transcription results")
        
        combined_result = transcription_processor.combine_transcriptions(chunk_results)
        
        combining_time = time.time() - combining_start
        st.info(f"⏱️ Combining took {combining_time:.2f} seconds")
        log_debug(f"Result combination completed in {combining_time:.2f}s")
        
        # Final status
        total_time = time.time() - init_start
        progress_bar.progress(1.0)
        status_text.text("✅ Transcription complete!")
        time_text.text(f"⏱️ Total processing time: {total_time:.2f} seconds")
        
        log_debug(f"Total processing time: {total_time:.2f}s")
        
        return combined_result
        
    except Exception as e:
        error_msg = f"Transcription process failed: {str(e)}"
        st.error(f"❌ {error_msg}")
        log_debug(error_msg, "ERROR")
        
        if st.session_state.debug_mode:
            st.markdown("### 🐛 Debug Information")
            st.code(traceback.format_exc())
        
        return None


def display_transcription_result(result: Dict[str, Any], settings: Dict[str, Any]):
    """Display transcription results with cloud debugging"""
    log_debug("Displaying transcription results")
    
    if not result or not result.get('success', False):
        st.error("❌ Transcription failed")
        if result and result.get('error'):
            st.error(f"Error: {result['error']}")
        log_debug("Transcription display failed", "ERROR")
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
    
    log_debug(f"Results displayed: {word_count} words, {result['chunk_count']} chunks")
    
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
    
    log_debug("Export options displayed successfully")


def test_api_connection(api_key: str):
    """Test OpenAI API connection with cloud debugging"""
    try:
        log_debug("Testing API connection")
        
        from whisper_client import WhisperClient
        
        st.info("🔍 Testing OpenAI API connection...")
        
        client = WhisperClient(api_key=api_key, model="whisper-1")
        
        # Test API key validation
        is_valid = client.validate_api_key()
        
        if is_valid:
            st.success("✅ API key is valid and working")
            log_debug("API connection test successful")
            
            # Show cost estimation
            cost_info = client.estimate_cost(60)  # 1 minute
            st.info(f"💰 Cost estimation for 1 minute: ${cost_info['estimated_cost_usd']}")
            
        else:
            st.error("❌ API key validation failed")
            log_debug("API connection test failed", "ERROR")
            
    except Exception as e:
        error_msg = f"API connection test failed: {str(e)}"
        st.error(f"❌ {error_msg}")
        log_debug(error_msg, "ERROR")


def main():
    """Main application function with cloud debugging"""
    try:
        log_debug("Starting main application")
        
        # Initialize session state
        initialize_session_state()
        
        # Display header
        display_header()
        
        # Display sidebar and get settings
        settings = display_sidebar()
        if not settings:
            st.stop()
        
        # Display file upload
        uploaded_file = display_file_upload()
        
        # Debug section
        with st.expander("🔧 Debug Tools", expanded=False):
            st.markdown("**Test API connection:**")
            
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
            <p>Deployed on Streamlit Cloud | For support, please contact the development team</p>
        </div>
        """, unsafe_allow_html=True)
        
        log_debug("Main application completed successfully")
        
    except Exception as e:
        error_msg = f"Main application failed: {str(e)}"
        st.error(f"❌ {error_msg}")
        log_debug(error_msg, "ERROR")
        
        if st.session_state.debug_mode:
            st.markdown("### 🐛 Debug Information")
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
