"""
Minimal Streamlit Audio Transcription App
Fallback version for deployment issues
"""

import streamlit as st
import os
import tempfile
from typing import Optional, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Audio Transcription App",
    page_icon="🎤",
    layout="wide"
)

def get_api_key() -> Optional[str]:
    """Get OpenAI API key from secrets or environment"""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key:
            return api_key
    except:
        pass
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    return None

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import openai
        return True, "OpenAI library available"
    except ImportError:
        return False, "OpenAI library not found. Please install: pip install openai"
    
    try:
        from pydub import AudioSegment
        return True, "Audio processing available"
    except ImportError:
        return False, "Audio processing not available. Please install: pip install pydub pyaudioop-lts"

def simple_transcribe(audio_file, api_key: str, language: Optional[str] = None):
    """Simple transcription without chunking"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(audio_file.read())
        temp_file.close()
        
        try:
            # Transcribe
            with open(temp_file.name, 'rb') as f:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language
                )
            
            return {
                'success': True,
                'text': response.text,
                'error': None
            }
        finally:
            # Clean up
            os.unlink(temp_file.name)
            
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'error': str(e)
        }

def main():
    """Main application function"""
    st.title("🎤 Audio Transcription App")
    st.markdown("**Powered by OpenAI Whisper**")
    
    # Check dependencies
    deps_ok, deps_msg = check_dependencies()
    if not deps_ok:
        st.error(f"⚠️ {deps_msg}")
        st.stop()
    
    # Check API key
    api_key = get_api_key()
    if not api_key:
        st.error("❌ OpenAI API key not found")
        st.info("Please configure your API key in Streamlit secrets or environment variables")
        st.stop()
    
    st.success("✅ All dependencies available")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
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
    
    # File upload
    st.header("📁 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'webm', 'mp4'],
        help="Supported formats: MP3, WAV, M4A, FLAC, OGG, WebM, MP4"
    )
    
    if uploaded_file is not None:
        st.info(f"📁 File: {uploaded_file.name} ({uploaded_file.size / (1024*1024):.1f} MB)")
        
        if st.button("🚀 Start Transcription", type="primary"):
            with st.spinner("Transcribing your audio file..."):
                result = simple_transcribe(uploaded_file, api_key, selected_language)
                
                if result['success']:
                    st.success("✅ Transcription complete!")
                    
                    # Display results
                    st.header("📝 Transcription Results")
                    st.text_area(
                        "Transcription",
                        value=result['text'],
                        height=400,
                        disabled=True
                    )
                    
                    # Download button
                    st.download_button(
                        "📄 Download as TXT",
                        data=result['text'],
                        file_name=f"transcription_{uploaded_file.name}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"❌ Transcription failed: {result['error']}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Built with ❤️ using Streamlit and OpenAI Whisper</p>
        <p>Minimal version for deployment compatibility</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
