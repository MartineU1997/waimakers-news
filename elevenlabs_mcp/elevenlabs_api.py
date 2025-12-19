"""
ElevenLabs API Client
=====================
Simple client for ElevenLabs text-to-speech API.
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any, List

# ElevenLabs API configuration
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Pre-made voices from ElevenLabs
DEFAULT_VOICES = {
    "rachel": {"id": "21m00Tcm4TlvDq8ikWAM", "description": "Calm, professional female"},
    "drew": {"id": "29vD33N1CtxCmqQRPOHJ", "description": "Confident male"},
    "clyde": {"id": "2EiwWnXFnvU5JabPnv8n", "description": "War veteran, deep male"},
    "paul": {"id": "5Q0t7uMcjvnagumLfvZi", "description": "News anchor male"},
    "domi": {"id": "AZnzlk1XvdvUeBnXmlld", "description": "Strong female"},
    "bella": {"id": "EXAVITQu4vr4xnSDxMaL", "description": "Soft female"},
    "antoni": {"id": "ErXwobaYiN019PkySvjV", "description": "Well-rounded male"},
    "josh": {"id": "TxGEqnHWrfWFTfGW9XjX", "description": "Deep male"},
    "arnold": {"id": "VR6AewLTigWG4xSOukaG", "description": "Crisp male"},
    "adam": {"id": "pNInz6obpgDQGcFmaJgB", "description": "Deep male"},
    "sam": {"id": "yoZ06aMxZJJ28mfd3POQ", "description": "Raspy male"},
}


def get_api_key() -> Optional[str]:
    """Get ElevenLabs API key from environment"""
    return os.environ.get("ELEVENLABS_API_KEY")


def list_voices(api_key: str) -> List[Dict[str, Any]]:
    """
    List available voices from ElevenLabs API.
    
    Returns both pre-made and user's cloned voices.
    """
    try:
        req = urllib.request.Request(
            f"{ELEVENLABS_API_URL}/voices",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("voices", [])
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code}")
        return []
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []


def get_voice_id(voice_name: str) -> str:
    """Get voice ID from name or return as-is if already an ID"""
    voice_info = DEFAULT_VOICES.get(voice_name.lower())
    if voice_info:
        return voice_info["id"]
    return voice_name  # Assume it's already an ID


def text_to_speech(
    text: str,
    api_key: str,
    voice: str = "rachel",
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.5,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        text: Text to convert to speech
        api_key: ElevenLabs API key
        voice: Voice name or ID
        model_id: Model to use
        stability: Voice stability (0-1)
        similarity_boost: Similarity boost (0-1)
        style: Style exaggeration (0-1)
        output_path: Path to save audio file
    
    Returns:
        Dict with success status and file info
    """
    voice_id = get_voice_id(voice)
    
    try:
        url = f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}"
        
        payload = json.dumps({
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            audio_data = response.read()
            
            # Generate filename if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.expanduser(f"~/Desktop/elevenlabs_audio_{timestamp}.mp3")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save audio
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            return {
                "success": True,
                "file_path": output_path,
                "file_size": len(audio_data),
                "voice": voice,
                "voice_id": voice_id,
                "text_length": len(text)
            }
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {
            "success": False,
            "error": f"API Error {e.code}: {error_body}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_user_info(api_key: str) -> Dict[str, Any]:
    """Get user subscription info and remaining credits"""
    try:
        req = urllib.request.Request(
            f"{ELEVENLABS_API_URL}/user/subscription",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}


def get_models(api_key: str) -> List[Dict[str, Any]]:
    """Get available TTS models"""
    try:
        req = urllib.request.Request(
            f"{ELEVENLABS_API_URL}/models",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return []
