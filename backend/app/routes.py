"""API routes for the TTS application with improved error handling."""

from flask import Blueprint, request, jsonify
from .errors import format_error_response, get_user_friendly_error
from .tts_engine import TTSEngine
import logging

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)
tts_engine = TTSEngine()

@api.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(format_error_response("Invalid request", 400)), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify(format_error_response("Text cannot be empty", 400)), 400
        
        # Check text length
        if len(text) > 5000:  # Example limit
            return jsonify(format_error_response("Text too long", 400)), 400
        
        language = data.get('language', 'en')
        model = data.get('model', 'default')
        
        # Generate audio
        audio_data = tts_engine.generate(text, language, model)
        
        return jsonify({
            "success": True,
            "data": {
                "audio": audio_data,
                "format": "wav"
            }
        })
        
    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        error_response = format_error_response(str(e), 500)
        return jsonify(error_response), 500

@api.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        is_ready = tts_engine.is_ready()
        
        if not is_ready:
            return jsonify(format_error_response("Engine not ready", 503)), 503
        
        return jsonify({
            "success": True,
            "data": {
                "status": "healthy",
                "engine_ready": True
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify(format_error_response(str(e), 500)), 500

@api.route('/api/models', methods=['GET'])
def get_models():
    """Get available TTS models."""
    try:
        models = tts_engine.get_available_models()
        
        if not models:
            return jsonify(format_error_response("Model not found", 404)), 404
        
        return jsonify({
            "success": True,
            "data": {
                "models": models
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get models: {str(e)}")
        return jsonify(format_error_response(str(e), 500)), 500