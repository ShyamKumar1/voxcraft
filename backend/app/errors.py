"""Error codes and user-friendly messages for the application."""

from enum import Enum
from typing import Dict, Optional, Tuple

class ErrorCode(str, Enum):
    """Enumeration of error codes for the application."""
    
    ENGINE_NOT_READY = "ENGINE_NOT_READY"
    EMPTY_TEXT = "EMPTY_TEXT"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    INVALID_LANGUAGE = "INVALID_LANGUAGE"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    AUDIO_GENERATION_FAILED = "AUDIO_GENERATION_FAILED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_REQUEST = "INVALID_REQUEST"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT = "TIMEOUT"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"

# Mapping of error messages (or patterns) to user-friendly messages and suggested actions
ERROR_MAPPINGS: Dict[str, Tuple[str, str, str]] = {
    "engine not ready": (
        ErrorCode.ENGINE_NOT_READY,
        "The TTS model is still downloading. This may take a minute on first run. Grab a coffee ☕",
        "Please wait a moment and try again. The model will be ready shortly."
    ),
    "text cannot be empty": (
        ErrorCode.EMPTY_TEXT,
        "Please enter some text to convert to speech.",
        "Type or paste the text you want to convert in the text input field."
    ),
    "text is empty": (
        ErrorCode.EMPTY_TEXT,
        "Please enter some text to convert to speech.",
        "Type or paste the text you want to convert in the text input field."
    ),
    "empty text": (
        ErrorCode.EMPTY_TEXT,
        "Please enter some text to convert to speech.",
        "Type or paste the text you want to convert in the text input field."
    ),
    "text too long": (
        ErrorCode.TEXT_TOO_LONG,
        "The text you entered is too long. Please shorten it.",
        "Try splitting your text into smaller chunks or reducing the length."
    ),
    "invalid language": (
        ErrorCode.INVALID_LANGUAGE,
        "The selected language is not supported.",
        "Please choose a language from the available options."
    ),
    "model not found": (
        ErrorCode.MODEL_NOT_FOUND,
        "The requested TTS model is not available.",
        "Please select a different model or check back later."
    ),
    "audio generation failed": (
        ErrorCode.AUDIO_GENERATION_FAILED,
        "Failed to generate audio. This might be due to a temporary issue.",
        "Please try again. If the problem persists, try a different text or model."
    ),
    "rate limit": (
        ErrorCode.RATE_LIMIT_EXCEEDED,
        "You've made too many requests. Please slow down.",
        "Wait a few seconds before trying again."
    ),
    "too many requests": (
        ErrorCode.RATE_LIMIT_EXCEEDED,
        "You've made too many requests. Please slow down.",
        "Wait a few seconds before trying again."
    ),
    "timeout": (
        ErrorCode.TIMEOUT,
        "The request took too long to complete.",
        "Please try again. If the problem persists, try a shorter text."
    ),
    "connection": (
        ErrorCode.NETWORK_ERROR,
        "Unable to connect to the server. Please check your internet connection.",
        "Check your internet connection and try again."
    ),
    "network": (
        ErrorCode.NETWORK_ERROR,
        "Unable to connect to the server. Please check your internet connection.",
        "Check your internet connection and try again."
    ),
    "unsupported format": (
        ErrorCode.UNSUPPORTED_FORMAT,
        "The requested audio format is not supported.",
        "Please select a different audio format from the available options."
    ),
}

def get_user_friendly_error(error_message: str) -> Dict:
    """
    Convert a raw error message to a user-friendly error response.
    
    Args:
        error_message: The raw error message from the system
        
    Returns:
        Dict containing error_code, message, and suggested_action
    """
    error_lower = error_message.lower()
    
    # Check for specific error patterns
    for pattern, (code, friendly_msg, action) in ERROR_MAPPINGS.items():
        if pattern in error_lower:
            return {
                "error_code": code,
                "message": friendly_msg,
                "suggested_action": action
            }
    
    # Default fallback for unknown errors
    return {
        "error_code": ErrorCode.INTERNAL_ERROR,
        "message": "An unexpected error occurred. Please try again.",
        "suggested_action": "If the problem persists, please contact support."
    }

def format_error_response(error_message: str, status_code: int = 500) -> Dict:
    """
    Format a complete error response with user-friendly message.
    
    Args:
        error_message: The raw error message
        status_code: HTTP status code (default: 500)
        
    Returns:
        Dict with error details suitable for API response
    """
    friendly_error = get_user_friendly_error(error_message)
    
    return {
        "success": False,
        "error": friendly_error,
        "status_code": status_code
    }