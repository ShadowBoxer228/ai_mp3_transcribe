"""
Configuration settings for the Streamlit Audio Transcription App
"""

import os
from typing import Dict, Any


class Config:
    """Application configuration class"""
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    WHISPER_MODEL = "whisper-1"
    
    # File Processing Configuration
    MAX_FILE_SIZE_MB = 500
    CHUNK_SIZE_MB = 24
    OVERLAP_SECONDS = 3
    
    # Supported audio formats
    SUPPORTED_FORMATS = {
        'mp3': 'mp3',
        'wav': 'wav', 
        'm4a': 'mp4',
        'flac': 'flac',
        'ogg': 'ogg',
        'webm': 'webm',
        'mp4': 'mp4',
        'mpeg': 'mp3',
        'mpga': 'mp3'
    }
    
    # Language options
    LANGUAGE_OPTIONS = {
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
    
    # API Configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # UI Configuration
    PAGE_TITLE = "Audio Transcription App"
    PAGE_ICON = "🎤"
    LAYOUT = "wide"
    
    @classmethod
    def get_streamlit_secrets(cls) -> Dict[str, Any]:
        """Get configuration from Streamlit secrets"""
        try:
            import streamlit as st
            return {
                'OPENAI_API_KEY': st.secrets.get("OPENAI_API_KEY"),
                'MAX_FILE_SIZE_MB': st.secrets.get("MAX_FILE_SIZE_MB", cls.MAX_FILE_SIZE_MB),
                'CHUNK_SIZE_MB': st.secrets.get("CHUNK_SIZE_MB", cls.CHUNK_SIZE_MB),
                'OVERLAP_SECONDS': st.secrets.get("OVERLAP_SECONDS", cls.OVERLAP_SECONDS),
            }
        except:
            return {}
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration from various sources"""
        config = {
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
            'WHISPER_MODEL': cls.WHISPER_MODEL,
            'MAX_FILE_SIZE_MB': cls.MAX_FILE_SIZE_MB,
            'CHUNK_SIZE_MB': cls.CHUNK_SIZE_MB,
            'OVERLAP_SECONDS': cls.OVERLAP_SECONDS,
            'SUPPORTED_FORMATS': cls.SUPPORTED_FORMATS,
            'LANGUAGE_OPTIONS': cls.LANGUAGE_OPTIONS,
            'MAX_RETRIES': cls.MAX_RETRIES,
            'RETRY_DELAY': cls.RETRY_DELAY,
            'PAGE_TITLE': cls.PAGE_TITLE,
            'PAGE_ICON': cls.PAGE_ICON,
            'LAYOUT': cls.LAYOUT,
        }
        
        # Override with Streamlit secrets if available
        secrets = cls.get_streamlit_secrets()
        config.update(secrets)
        
        return config
