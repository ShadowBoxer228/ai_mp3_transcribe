@echo off

REM Set the OpenAI API key (replace with your actual API key)
set OPENAI_API_KEY=your-api-key-here

REM Run the Streamlit app
echo 🚀 Starting Audio Transcription App...
echo 📱 Local URL: http://localhost:8501
echo.
echo ⚠️  Note: Replace 'your-api-key-here' with your actual OpenAI API key
echo 🎤 Ready to transcribe audio files!
echo.

streamlit run app.py
