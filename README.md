# 🎤 Streamlit Audio Transcription App

A powerful web application that transcribes audio files of any size using OpenAI's Whisper API. The app automatically handles large files by splitting them into chunks, processes each chunk, and combines the results into a complete transcription with timestamps.

## ✨ Features

### Core Functionality
- **Multi-format Support**: MP3, WAV, M4A, FLAC, OGG, WebM, MP4, MPEG, MPGA
- **Intelligent Chunking**: Automatically splits large files (>25MB) into optimal chunks
- **Smart Segmentation**: Uses silence detection to split at natural breaks
- **Overlap Handling**: Adds overlap between chunks to avoid word cutoffs
- **Real-time Progress**: Live progress tracking for upload, processing, and transcription
- **Multiple Export Formats**: TXT, SRT, VTT, and JSON formats

### Advanced Features
- **Language Detection**: Automatic language detection or manual selection
- **Timestamp Support**: Detailed timestamps for segments and words
- **Error Handling**: Robust error handling with retry logic
- **Cost Estimation**: Real-time cost estimation for API usage
- **Responsive UI**: Clean, modern interface with progress indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- FFmpeg (for audio processing)

### Installation

1. **Clone or download the project files**
   ```bash
   # If you have the files locally, navigate to the directory
   cd "ai transcript"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (required for audio processing)
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Windows:**
   Download from [FFmpeg website](https://ffmpeg.org/download.html)
   
   **Linux:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

4. **Configure API Key**
   
   **Option 1: Use the run scripts (recommended)**
   - Edit `run_local.sh` (macOS/Linux) or `run_local.bat` (Windows)
   - Replace `your-api-key-here` with your actual OpenAI API key
   
   **Option 2: Environment Variable**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   **Option 3: Streamlit Secrets** (for cloud deployment)
   The API key is already configured in `.streamlit/secrets.toml` for cloud deployment.

5. **Run the application**
   
   **macOS/Linux:**
   ```bash
   ./run_local.sh
   ```
   
   **Windows:**
   ```cmd
   run_local.bat
   ```
   
   **Manual method:**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8501`

## 🌐 Cloud Deployment

### **Streamlit Cloud (Recommended)**

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with your GitHub account**
3. **Click "New app"**
4. **Fill in:**
   - **Repository**: `ShadowBoxer228/ai_mp3_transcribe`
   - **Branch**: `main`
   - **Main file path**: `app_cloud.py`
5. **Click "Deploy!"**

The app will be available at: `https://your-app-name.streamlit.app`

### **Cloud Features**
- ✅ **Enhanced debugging** with real-time logs
- ✅ **Performance monitoring** for each step
- ✅ **Error recovery** with detailed stack traces
- ✅ **Debug mode toggle** in sidebar
- ✅ **API connection testing**
- ✅ **Cloud-optimized processing**

For detailed deployment instructions, see [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)

## 📁 Project Structure

```
streamlit_transcription_app/
├── app.py                    # Main Streamlit application
├── audio_processor.py        # Audio handling and chunking
├── whisper_client.py         # OpenAI Whisper API integration
├── transcription_utils.py    # Text processing and export utilities
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── secrets.toml         # API keys and secrets
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Streamlit Secrets
Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-api-key-here"
MAX_FILE_SIZE_MB = 500
CHUNK_SIZE_MB = 24
OVERLAP_SECONDS = 3
```

### App Settings
- **Chunk Size**: Maximum size for each audio chunk (10-24 MB)
- **Overlap**: Overlap between chunks to avoid word cutoffs (1-5 seconds)
- **Language**: Auto-detect or specify language for better accuracy
- **Timestamps**: Include timestamps in output

## 🎯 Usage Guide

### Basic Usage

1. **Upload Audio File**
   - Click "Choose an audio file" or drag and drop
   - Supported formats: MP3, WAV, M4A, FLAC, OGG, WebM, MP4
   - Maximum file size: 500MB

2. **Configure Settings** (Optional)
   - Select language if known
   - Adjust chunk size and overlap settings
   - Choose whether to show timestamps

3. **Start Transcription**
   - Click "🚀 Start Transcription"
   - Monitor progress in real-time
   - Wait for processing to complete

4. **View Results**
   - Review transcription in the text area
   - Check statistics (duration, word count, etc.)
   - Download in your preferred format

### Advanced Features

#### Language Selection
- **Auto-detect**: Let Whisper determine the language
- **Manual Selection**: Choose from supported languages for better accuracy
- **Supported Languages**: English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese

#### Export Formats
- **TXT**: Plain text with optional timestamps
- **SRT**: SubRip subtitle format for video editing
- **VTT**: WebVTT format for web applications
- **JSON**: Complete data with metadata and word-level timestamps

#### Large File Processing
- Files >25MB are automatically split into chunks
- Smart segmentation uses silence detection
- Overlap prevents word cutoffs between chunks
- Progress tracking shows current chunk being processed

## 🔍 Technical Details

### Audio Processing
- **Format Conversion**: Automatic conversion to MP3 for API compatibility
- **Quality Preservation**: Maintains audio quality during processing
- **Silence Detection**: Intelligent splitting at natural pauses
- **Overlap Management**: Configurable overlap to prevent word loss

### API Integration
- **Retry Logic**: Automatic retry on API failures
- **Rate Limiting**: Respects OpenAI rate limits
- **Error Handling**: Comprehensive error messages
- **Cost Tracking**: Real-time cost estimation

### Performance Optimizations
- **Streaming Upload**: Efficient handling of large files
- **Memory Management**: Optimized memory usage for large files
- **Parallel Processing**: Ready for future parallel chunk processing
- **Caching**: Session state management for better UX

## 🛠️ Troubleshooting

### Common Issues

#### "API Key not found"
- Ensure your OpenAI API key is properly configured
- Check environment variables or Streamlit secrets
- Verify the key is valid and has sufficient credits

#### "FFmpeg not found"
- Install FFmpeg on your system
- Ensure FFmpeg is in your system PATH
- Restart your terminal/IDE after installation

#### "File format not supported"
- Check that your file is in a supported format
- Try converting to MP3 or WAV format
- Ensure the file is not corrupted

#### "Transcription failed"
- Check your internet connection
- Verify your OpenAI API key has sufficient credits
- Try with a smaller file first
- Check the error message for specific details

#### Large file processing issues
- Ensure sufficient disk space for temporary files
- Check available memory
- Try reducing chunk size in settings
- Consider processing smaller segments

### Performance Tips

1. **Optimize File Size**
   - Use compressed formats (MP3) for large files
   - Consider reducing audio quality if transcription accuracy allows

2. **Network Considerations**
   - Ensure stable internet connection
   - Consider processing during off-peak hours

3. **Resource Management**
   - Close other applications during processing
   - Ensure sufficient RAM for large files

## 🔒 Security & Privacy

### Data Handling
- Audio files are processed locally before API calls
- Temporary files are automatically cleaned up
- No audio data is stored permanently
- API calls are made directly to OpenAI

### API Key Security
- Store API keys in environment variables or Streamlit secrets
- Never commit API keys to version control
- Use separate API keys for development and production

### Privacy Considerations
- Audio content is sent to OpenAI for processing
- Review OpenAI's privacy policy before use
- Consider data sensitivity when processing confidential audio

## 📊 Cost Estimation

### OpenAI Whisper Pricing
- **Cost**: $0.006 per minute of audio
- **Example**: 1 hour of audio ≈ $0.36

### Cost Factors
- Audio duration (primary factor)
- Number of chunks (minimal impact)
- Retry attempts (only if failures occur)

### Cost Optimization
- Use appropriate audio quality (not unnecessarily high)
- Process during off-peak hours for better API performance
- Monitor usage through OpenAI dashboard

## 🚀 Deployment

### Streamlit Community Cloud

1. **Prepare for deployment**
   ```bash
   # Ensure all files are in the repository
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set environment variables in the dashboard
   - Deploy the app

3. **Configure secrets**
   - Add `OPENAI_API_KEY` in the Streamlit Cloud dashboard
   - Set other configuration variables as needed

### Other Platforms

#### Heroku
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
git push heroku main
```

#### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Include error handling

### Testing
- Test with various audio formats and sizes
- Verify error handling scenarios
- Check UI responsiveness
- Validate export functionality

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

### Getting Help
- Check the troubleshooting section above
- Review OpenAI's documentation
- Check Streamlit documentation for UI issues
- Open an issue on the project repository

### Feature Requests
- Submit feature requests through GitHub issues
- Provide detailed descriptions of desired functionality
- Consider contributing the feature yourself

## 🔄 Updates & Maintenance

### Regular Updates
- Keep dependencies updated
- Monitor OpenAI API changes
- Update documentation as needed
- Test with new audio formats

### Version History
- **v1.0.0**: Initial release with core functionality
- Future versions will include additional features and improvements

---

**Built with ❤️ using Streamlit and OpenAI Whisper**

For questions, issues, or contributions, please visit the project repository or contact the development team.
