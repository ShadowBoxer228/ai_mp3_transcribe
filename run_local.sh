#!/bin/bash

# Set the OpenAI API key (replace with your actual API key)
export OPENAI_API_KEY='your-api-key-here'

# Run the Streamlit app
echo "🚀 Starting Audio Transcription App..."
echo "📱 Local URL: http://localhost:8501"
echo "🌐 Network URL: http://192.168.1.104:8501"
echo ""
echo "⚠️  Note: Replace 'your-api-key-here' with your actual OpenAI API key"
echo "🎤 Ready to transcribe audio files!"
echo ""

streamlit run app.py
