import React from 'react';
import { getFriendlyError } from '../utils/errorHandler';

/**
 * Component to display user-friendly error messages with suggested actions.
 */
const ErrorDisplay = ({ error, onRetry, className = '' }) => {
  if (!error) return null;
  
  const friendlyError = getFriendlyError(error);
  
  return (
    <div className={`error-display ${className}`}>
      <div className="error-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M12 16H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      
      <div className="error-content">
        <h3 className="error-title">Something went wrong</h3>
        <p className="error-message">{friendlyError.message}</p>
        
        {friendlyError.suggestedAction && (
          <div className="error-action">
            <p className="error-suggestion">
              <strong>Suggested action:</strong> {friendlyError.suggestedAction}
            </p>
          </div>
        )}
        
        {onRetry && (
          <button 
            className="error-retry-button"
            onClick={onRetry}
            aria-label="Retry the operation"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorDisplay;