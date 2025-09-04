# 🚀 Streamlit Cloud Setup Guide

## 📋 Quick Setup Steps

### 1. Deploy the Cloud-Optimized Version

**Recommended:** Use `app_cloud.py` for Streamlit Cloud deployment:

1. **Go to Streamlit Cloud** and create a new app
2. **Set main file path to:** `app_cloud.py`
3. **This version is specifically optimized for cloud deployment**

### 2. Configure API Key in Streamlit Cloud

1. **Go to your deployed app** on Streamlit Cloud
2. **Click the gear icon (⚙️)** in the bottom right corner
3. **Go to "Secrets" tab**
4. **Add the following configuration:**

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

**Note:** Replace `"your-openai-api-key-here"` with your actual OpenAI API key. You can find your API key in the project files or get a new one from [OpenAI Platform](https://platform.openai.com/api-keys).

### 3. Save and Restart

1. **Click "Save"** in the secrets configuration
2. **The app will automatically restart** with the new configuration
3. **Refresh your browser** to see the changes

## 📊 App Versions

### Cloud-Optimized Version (`app_cloud.py`)
- ✅ **Designed for Streamlit Cloud** - No dependency issues
- ✅ **Simple, reliable transcription** - Works consistently
- ✅ **Environment detection** - Adapts to cloud vs local
- ✅ **Simplified UI** - Clean, cloud-friendly interface
- ✅ **Basic export options** - TXT and JSON formats

### Full-Featured Version (`app.py`)
- ✅ **Advanced audio processing** - Chunking, silence detection
- ✅ **Multiple export formats** - TXT, SRT, VTT, JSON
- ✅ **Debug tools** - Comprehensive logging and testing
- ✅ **Local development** - Best for local testing

## ✅ Expected Results

After configuring the API key, you should see:
- ✅ **Green checkmark** instead of "API Key not found"
- ✅ **File upload interface** becomes available
- ✅ **Transcription functionality** is ready to use

## 🎯 How to Use

1. **Upload an audio file** (MP3, WAV, M4A, FLAC, OGG, WebM, MP4)
2. **Click "Start Transcription"**
3. **Wait for processing** (may take 30 seconds to several minutes)
4. **Download the results** in your preferred format

## ⚠️ Important Notes

### Audio Processing Limitations
- The app shows "Audio Processing Limited" - this is normal
- **Basic transcription works perfectly** without full audio processing
- **Large files** may take longer to process
- **No chunking** is available in this mode (files are processed as-is)

### File Size Limits
- **Maximum file size**: 25MB (OpenAI Whisper limit)
- **Recommended**: Keep files under 10MB for faster processing
- **Supported formats**: MP3, WAV, M4A, FLAC, OGG, WebM, MP4

## 🔧 Troubleshooting

### If API Key Still Shows as "Not Found"
1. **Check the secrets configuration** - make sure there are no extra spaces
2. **Restart the app** - click the restart button in Streamlit Cloud
3. **Clear browser cache** and refresh the page

### If Transcription Fails
1. **Check file size** - must be under 25MB
2. **Check file format** - must be a supported audio format
3. **Check API quota** - ensure you have OpenAI credits available

### If App Won't Start
1. **Check the logs** in Streamlit Cloud dashboard
2. **Verify repository** has all required files
3. **Try the minimal app** (`app_minimal.py`) as fallback

## 📊 Cost Information

### OpenAI Whisper Pricing
- **Cost**: $0.006 per minute of audio
- **Example**: 10 minutes of audio ≈ $0.06
- **Monitor usage** in your OpenAI dashboard

### Example Costs
- 1 minute audio: ~$0.006
- 5 minutes audio: ~$0.03
- 10 minutes audio: ~$0.06
- 1 hour audio: ~$0.36

## 🎉 Success!

Once configured, your app will be fully functional for audio transcription. The "Audio Processing Limited" warning is normal and doesn't affect the core functionality.

---

**Need Help?** Check the main README.md for detailed documentation or create an issue in the repository.
