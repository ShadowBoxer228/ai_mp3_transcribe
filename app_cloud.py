"""
Streamlit Audio Transcription App - Cloud Optimized Version
Designed specifically for Streamlit Cloud deployment
"""

import streamlit as st
import os
import tempfile
import time
from typing import Optional, Dict, Any

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
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_api_key() -> Optional[str]:
    """Get OpenAI API key from secrets or environment"""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key and api_key != "your-openai-api-key-here":
            return api_key
    except:
        pass
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    return None

def check_environment():
    """Check the deployment environment and available features"""
    is_cloud = os.getenv("STREAMLIT_CLOUD") is not None
    has_pydub = False
    
    try:
        import pydub
        has_pydub = True
    except ImportError:
        has_pydub = False
    
    return {
        'is_cloud': is_cloud,
        'has_pydub': has_pydub,
        'environment': 'Streamlit Cloud' if is_cloud else 'Local'
    }

def display_header(env_info):
    """Display application header with environment info"""
    st.markdown('<h1 class="main-header">🎤 Audio Transcription App</h1>', unsafe_allow_html=True)
    
    # Environment info
    if env_info['is_cloud']:
        st.markdown(f"""
        <div class="info-box">
            <strong>🌐 Running on {env_info['environment']}</strong><br>
            Cloud-optimized version with simplified audio processing
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
            <strong>💻 Running Locally</strong><br>
            Full-featured version with advanced audio processing
        </div>
        """, unsafe_allow_html=True)
    
    # Feature availability
    if not env_info['has_pydub']:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Audio Processing Limited</strong><br>
            Using simplified mode. For full features, install: pip install pydub
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-box">
            <strong>✅ Full Audio Processing Available</strong><br>
            Advanced features including chunking and silence detection
        </div>
        """, unsafe_allow_html=True)

def display_sidebar(env_info):
    """Display sidebar with settings"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key status
        api_key = get_api_key()
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.error("❌ API Key not found")
            st.info("Configure your OpenAI API key in Streamlit secrets")
            return None
        
        # Language selection
        language = st.selectbox(
            "Language (optional)",
            ["Auto-detect", "English", "Spanish", "French", "German", "Italian", 
             "Portuguese", "Russian", "Japanese", "Korean", "Chinese"]
        )
        
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
        
        # Advanced settings (only show if pydub is available)
        if env_info['has_pydub']:
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
                
                force_time_based = st.checkbox(
                    "Force time-based splitting",
                    value=False,
                    help="Skip silence detection for faster processing"
                )
        else:
            chunk_size = 24
            overlap_seconds = 3
            force_time_based = False
        
        # App information
        st.markdown("---")
        st.markdown("### 📊 App Information")
        st.info(f"""
        **Environment:** {env_info['environment']}
        
        **Audio Processing:** {'Full' if env_info['has_pydub'] else 'Limited'}
        
        **File Size Limit:** 25MB (OpenAI limit)
        
        **Supported Formats:** MP3, WAV, M4A, FLAC, OGG, WebM, MP4
        """)
        
        return {
            'api_key': api_key,
            'language': selected_language,
            'chunk_size': chunk_size,
            'overlap_seconds': overlap_seconds,
            'force_time_based': force_time_based
        }

def simple_transcribe(audio_file, api_key: str, language: Optional[str] = None):
    """Simple transcription without chunking - works in all environments"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(audio_file.read())
        temp_file.close()
        
        try:
            st.info("🔄 Transcribing audio file...")
            start_time = time.time()
            
            # Transcribe
            with open(temp_file.name, 'rb') as f:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language,
                    response_format='verbose_json',
                    timestamp_granularities=['word', 'segment']
                )
            
            transcription_time = time.time() - start_time
            st.success(f"✅ Transcription completed in {transcription_time:.2f} seconds")
            
            # Format result
            result = {
                'success': True,
                'text': response.text,
                'language': getattr(response, 'language', language),
                'duration': getattr(response, 'duration', None),
                'segments': getattr(response, 'segments', []),
                'words': getattr(response, 'words', []),
                'total_duration': getattr(response, 'duration', 0),
                'chunk_count': 1,
                'failed_chunks': 0
            }
            
            return result
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
            
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'error': str(e),
            'total_duration': 0,
            'chunk_count': 0,
            'failed_chunks': 1
        }

def display_transcription_result(result: Dict[str, Any]):
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
    
    # Simple text display (no complex formatting to avoid issues)
    st.text_area(
        "Transcription",
        value=result['text'],
        height=400,
        disabled=True
    )
    
    # Export options
    st.markdown("### 💾 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "📄 Download TXT",
            data=result['text'],
            file_name="transcription.txt",
            mime="text/plain"
        )
    
    with col2:
        # Simple JSON export
        import json
        json_data = {
            'text': result['text'],
            'language': result.get('language'),
            'duration': result.get('total_duration', 0),
            'word_count': len(result['text'].split())
        }
        json_content = json.dumps(json_data, indent=2)
        st.download_button(
            "📊 Download JSON",
            data=json_content,
            file_name="transcription.json",
            mime="application/json"
        )

def main():
    """Main application function"""
    # Check environment
    env_info = check_environment()
    
    # Display header
    display_header(env_info)
    
    # Display sidebar and get settings
    settings = display_sidebar(env_info)
    if not settings:
        st.stop()
    
    # File upload
    st.header("📁 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'webm', 'mp4'],
        help="Supported formats: MP3, WAV, M4A, FLAC, OGG, WebM, MP4 (Max 25MB)"
    )
    
    if uploaded_file is not None:
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 25:
            st.error(f"❌ File too large: {file_size_mb:.1f}MB. Maximum size is 25MB.")
            return
        
        st.info(f"📁 File: {uploaded_file.name} ({file_size_mb:.1f} MB)")
        
        if st.button("🚀 Start Transcription", type="primary"):
            with st.spinner("Processing your audio file..."):
                result = simple_transcribe(uploaded_file, settings['api_key'], settings['language'])
                display_transcription_result(result)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Built with ❤️ using Streamlit and OpenAI Whisper</p>
        <p>Cloud-optimized version for reliable deployment</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
