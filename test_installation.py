"""
Test script to verify installation and dependencies
Run this script to check if all required packages are installed correctly
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'streamlit',
        'openai', 
        'pydub',
        'dotenv'
    ]
    
    print("🔍 Testing package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError as e:
            print(f"❌ {package} - FAILED: {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("\n🔍 Testing FFmpeg availability...")
    try:
        from pydub.utils import which
        ffmpeg_path = which("ffmpeg")
        if ffmpeg_path:
            print(f"✅ FFmpeg found at: {ffmpeg_path}")
            return True
        else:
            print("❌ FFmpeg not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False

def test_openai_api():
    """Test OpenAI API key configuration"""
    print("\n🔍 Testing OpenAI API configuration...")
    
    # Check environment variable
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key found in environment variables")
        return True
    
    # Check Streamlit secrets
    try:
        import streamlit as st
        # This will only work if running in Streamlit context
        print("ℹ️  Streamlit secrets check requires running in Streamlit context")
        return False
    except:
        print("❌ OpenAI API key not found in environment variables")
        print("   Please set OPENAI_API_KEY environment variable or configure Streamlit secrets")
        return False

def main():
    """Main test function"""
    print("🧪 Streamlit Audio Transcription App - Installation Test")
    print("=" * 60)
    
    # Test Python version
    print(f"🐍 Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("⚠️  Warning: Python 3.8 or higher is recommended")
    else:
        print("✅ Python version is compatible")
    
    # Test package imports
    failed_imports = test_imports()
    
    # Test FFmpeg
    ffmpeg_ok = test_ffmpeg()
    
    # Test OpenAI API
    api_ok = test_openai_api()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    if not failed_imports and ffmpeg_ok and api_ok:
        print("🎉 All tests passed! Your installation is ready.")
        print("\n🚀 You can now run the app with:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some issues found:")
        
        if failed_imports:
            print(f"   - Missing packages: {', '.join(failed_imports)}")
            print("   - Run: pip install -r requirements.txt")
        
        if not ffmpeg_ok:
            print("   - FFmpeg not found")
            print("   - Install FFmpeg: https://ffmpeg.org/download.html")
        
        if not api_ok:
            print("   - OpenAI API key not configured")
            print("   - Set OPENAI_API_KEY environment variable")

if __name__ == "__main__":
    main()
