/**
 * Utility functions for handling and displaying user-friendly error messages.
 */

/**
 * Get user-friendly error message from API response
 * @param {Object} error - The error object from API call
 * @returns {Object} Object with message and suggestedAction
 */
export function getFriendlyError(error) {
  // If the error has a structured response from our backend
  if (error.response?.data?.error) {
    const { message, suggested_action } = error.response.data.error;
    return {
      message: message || 'An unexpected error occurred.',
      suggestedAction: suggested_action || 'Please try again.',
      errorCode: error.response.data.error.error_code
    };
  }
  
  // Handle network errors
  if (error.message === 'Network Error') {
    return {
      message: 'Unable to connect to the server. Please check your internet connection.',
      suggestedAction: 'Check your internet connection and try again.',
      errorCode: 'NETWORK_ERROR'
    };
  }
  
  // Handle timeout errors
  if (error.code === 'ECONNABORTED') {
    return {
      message: 'The request took too long to complete.',
      suggestedAction: 'Please try again. If the problem persists, try a shorter text.',
      errorCode: 'TIMEOUT'
    };
  }
  
  // Fallback for unknown errors
  return {
    message: error.message || 'An unexpected error occurred.',
    suggestedAction: 'Please try again. If the problem persists, contact support.',
    errorCode: 'UNKNOWN_ERROR'
  };
}

/**
 * Show error toast with user-friendly message
 * @param {Object} error - The error object
 * @param {Function} showToast - Toast notification function
 */
export function showErrorToast(error, showToast) {
  const friendlyError = getFriendlyError(error);
  
  showToast({
    type: 'error',
    title: 'Error',
    message: friendlyError.message,
    description: friendlyError.suggestedAction,
    duration: 5000, // 5 seconds
    action: friendlyError.suggestedAction ? {
      label: friendlyError.suggestedAction,
      onClick: () => {} // Could add retry logic here
    } : null
  });
}