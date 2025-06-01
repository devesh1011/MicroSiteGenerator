import React from 'react';
import { Eye, Share2, RefreshCcw, Trash2 } from 'lucide-react';
import { ActionType, Demo } from '../types';

interface ActionButtonsProps {
  demo: Demo;
  onAction: (type: ActionType, demo: Demo) => void;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({ demo, onAction }) => {
  const { status, micrositeUrl } = demo;

  const handleViewClick = () => {
    if (micrositeUrl) {
      window.open(micrositeUrl, '_blank');
    } else {
      console.warn('Microsite URL not available for viewing.', demo);
    }
  };

  return (
    <div className="flex space-x-2">
      {status === 'Ready' && (
        <>
          <button
            onClick={handleViewClick}
            className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
            title="View Microsite"
            disabled={!micrositeUrl}
          >
            <Eye className="h-4 w-4" />
          </button>
          <button
            onClick={() => onAction('share', demo)}
            className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
            title="Share Microsite"
          >
            <Share2 className="h-4 w-4" />
          </button>
        </>
      )}
      
      {status === 'Failed' && (
        <button
          onClick={() => onAction('regenerate', demo)}
          className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
          title="Re-generate Microsite"
        >
          <RefreshCcw className="h-4 w-4" />
        </button>
      )}
      
      {(status === 'Ready' || status === 'Failed') && (
        <button
          onClick={() => onAction('delete', demo)}
          className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
          title="Delete Demo"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      )}
    </div>
  );
};

export default ActionButtons;