import React from 'react';
import { CheckCircle, Loader2, XCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: 'Ready' | 'Processing' | 'Failed';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  switch (status) {
    case 'Ready':
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle className="h-3.5 w-3.5 mr-1" />
          Ready
        </span>
      );
    case 'Processing':
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />
          Processing
        </span>
      );
    case 'Failed':
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <XCircle className="h-3.5 w-3.5 mr-1" />
          Failed
        </span>
      );
    default:
      return null;
  }
};

export default StatusBadge;