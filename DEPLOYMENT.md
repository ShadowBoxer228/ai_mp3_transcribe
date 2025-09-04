# 🚀 Streamlit Cloud Deployment Guide

This guide will help you deploy the Audio Transcription App to Streamlit Cloud.

## 📋 Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **OpenAI API Key**: Get your API key from [OpenAI Platform](https://platform.openai.com)

## 🔧 Deployment Steps

### 1. Prepare Your Repository

Ensure your repository contains:
- ✅ `app.py` (main application)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `packages.txt` (system dependencies)
- ✅ All supporting modules

### 2. Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)
2. **Sign in**: Use your GitHub account
3. **New App**: Click "New app"
4. **Repository**: Select your repository
5. **Branch**: Choose `main` branch
6. **Main file path**: Enter `app.py`
7. **Deploy**: Click "Deploy!"

### 3. Configure Secrets

After deployment, configure your API key:

1. **Go to App Settings**: Click the gear icon in your app
2. **Secrets**: Add the following to your secrets:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

### 4. System Dependencies

The app automatically installs required system packages via `packages.txt`:
- `ffmpeg` - Audio processing
- `libsndfile1` - Audio file support

## 🐛 Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: pyaudioop
**Solution**: The `pyaudioop-lts` package is included in requirements.txt to fix this issue.

#### 2. FFmpeg Not Found
**Solution**: The `packages.txt` file installs FFmpeg automatically.

#### 3. Audio Processing Errors
**Solution**: Check that all dependencies are properly installed:
```bash
pip install pydub pyaudioop-lts
```

### Debug Mode

The app includes built-in debugging tools:
1. **Test API Connection**: Verify your OpenAI API key
2. **Create Test Audio**: Generate test files for debugging
3. **Detailed Logging**: Comprehensive error messages

## 📊 Performance Tips

### For Large Files
- Use "Force time-based splitting" for faster processing
- Reduce chunk size if experiencing memory issues
- Monitor API usage and costs

### For Better Accuracy
- Specify the correct language in settings
- Use higher quality audio files
- Enable silence detection for natural speech

## 🔒 Security

### API Key Management
- Never commit API keys to your repository
- Use Streamlit Cloud secrets for secure storage
- Monitor your OpenAI usage regularly

### File Handling
- Audio files are processed in memory
- Temporary files are automatically cleaned up
- No audio data is permanently stored

## 📈 Monitoring

### App Performance
- Check Streamlit Cloud logs for errors
- Monitor API response times
- Track memory usage for large files

### Cost Management
- Monitor OpenAI API usage
- Set usage limits in OpenAI dashboard
- Use cost estimation features in the app

## 🆘 Support

### Getting Help
1. Check the app's debug tools
2. Review Streamlit Cloud logs
3. Test with small audio files first
4. Verify API key permissions

### Common Solutions
- **App won't start**: Check requirements.txt and packages.txt
- **Audio processing fails**: Verify FFmpeg installation
- **API errors**: Check API key and quota limits
- **Slow processing**: Use time-based splitting for large files

## 🔄 Updates

To update your deployed app:
1. Push changes to your GitHub repository
2. Streamlit Cloud automatically redeploys
3. Check the deployment status in your dashboard

## 📝 Example Configuration

### Complete secrets.toml
```toml
OPENAI_API_KEY = "sk-proj-your-key-here"
MAX_FILE_SIZE_MB = 500
CHUNK_SIZE_MB = 24
OVERLAP_SECONDS = 3
```

### Environment Variables (Alternative)
If you prefer environment variables:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
```

## 🎯 Best Practices

1. **Test Locally First**: Always test changes locally before deploying
2. **Monitor Costs**: Keep track of OpenAI API usage
3. **Use Debug Tools**: Leverage built-in debugging features
4. **Regular Updates**: Keep dependencies up to date
5. **Error Handling**: The app includes comprehensive error handling

## 📞 Need Help?

- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **OpenAI API Docs**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **GitHub Issues**: Create an issue in your repository

---

**Happy Deploying! 🚀**
