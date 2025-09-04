"""
Demo script showing how to use the transcription components
This script demonstrates the core functionality without the Streamlit UI
"""

import os
import sys
from audio_processor import AudioProcessor
from whisper_client import WhisperClient
from transcription_utils import TranscriptionProcessor, TranscriptionExporter

def demo_audio_processing():
    """Demonstrate audio processing functionality"""
    print("🎵 Audio Processing Demo")
    print("-" * 30)
    
    # Initialize audio processor
    processor = AudioProcessor(max_chunk_size_mb=24, overlap_seconds=3)
    
    # Show supported formats
    print(f"Supported formats: {', '.join(processor.SUPPORTED_FORMATS.keys())}")
    print(f"Max chunk size: {processor.max_chunk_size_mb}MB")
    print(f"Overlap: {processor.overlap_seconds} seconds")
    
    return processor

def demo_whisper_client():
    """Demonstrate Whisper client functionality"""
    print("\n🤖 Whisper Client Demo")
    print("-" * 30)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found")
        print("   Set OPENAI_API_KEY environment variable to test Whisper client")
        return None
    
    # Initialize client
    client = WhisperClient(api_key=api_key, model="whisper-1")
    
    # Test API key validation
    print("🔑 Validating API key...")
    is_valid = client.validate_api_key()
    if is_valid:
        print("✅ API key is valid")
    else:
        print("❌ API key validation failed")
        return None
    
    # Show cost estimation
    print("\n💰 Cost estimation for 1 hour of audio:")
    cost_info = client.estimate_cost(3600)  # 1 hour
    print(f"   Duration: {cost_info['duration_minutes']:.1f} minutes")
    print(f"   Estimated cost: ${cost_info['estimated_cost_usd']}")
    
    return client

def demo_transcription_utils():
    """Demonstrate transcription utilities"""
    print("\n📝 Transcription Utils Demo")
    print("-" * 30)
    
    # Initialize components
    processor = TranscriptionProcessor()
    exporter = TranscriptionExporter()
    
    # Sample transcription data
    sample_transcription = {
        'text': 'Hello, this is a sample transcription with timestamps.',
        'language': 'en',
        'total_duration': 5.2,
        'segments': [
            {
                'start': 0.0,
                'end': 2.1,
                'text': 'Hello, this is a sample'
            },
            {
                'start': 2.1,
                'end': 5.2,
                'text': 'transcription with timestamps.'
            }
        ],
        'words': [
            {'start': 0.0, 'end': 0.5, 'word': 'Hello'},
            {'start': 0.5, 'end': 0.8, 'word': ','},
            {'start': 0.8, 'end': 1.2, 'word': 'this'},
            {'start': 1.2, 'end': 1.4, 'word': 'is'},
            {'start': 1.4, 'end': 1.6, 'word': 'a'},
            {'start': 1.6, 'end': 2.1, 'word': 'sample'}
        ],
        'chunk_count': 1,
        'success': True
    }
    
    # Format with timestamps
    formatted_text = processor.format_transcription_with_timestamps(sample_transcription, True)
    print("📄 Formatted transcription with timestamps:")
    print(formatted_text)
    
    # Export examples
    print("\n📤 Export examples:")
    
    # TXT export
    txt_content = exporter.export_to_txt(sample_transcription, include_timestamps=True)
    print(f"TXT length: {len(txt_content)} characters")
    
    # SRT export
    srt_content = exporter.export_to_srt(sample_transcription)
    print(f"SRT length: {len(srt_content)} characters")
    
    # VTT export
    vtt_content = exporter.export_to_vtt(sample_transcription)
    print(f"VTT length: {len(vtt_content)} characters")
    
    # JSON export
    json_content = exporter.export_to_json(sample_transcription)
    print(f"JSON length: {len(json_content)} characters")
    
    return processor, exporter

def main():
    """Main demo function"""
    print("🎤 Streamlit Audio Transcription App - Component Demo")
    print("=" * 60)
    
    # Demo audio processing
    audio_processor = demo_audio_processing()
    
    # Demo Whisper client
    whisper_client = demo_whisper_client()
    
    # Demo transcription utilities
    transcription_processor, exporter = demo_transcription_utils()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Demo Summary:")
    print("✅ Audio processing components loaded")
    if whisper_client:
        print("✅ Whisper client ready")
    else:
        print("⚠️  Whisper client not available (API key required)")
    print("✅ Transcription utilities ready")
    
    print("\n🚀 To run the full app:")
    print("   streamlit run app.py")
    
    print("\n🧪 To test installation:")
    print("   python test_installation.py")

if __name__ == "__main__":
    main()
