import React, { useRef } from 'react';
import { UploadCloud, PlusCircle, ExternalLink } from 'lucide-react';

interface QuickActionsProps {
  onUploadDemo: () => void;
  onProcessFile: (file: File) => void;
}

const QuickActions: React.FC<QuickActionsProps> = ({ onUploadDemo, onProcessFile }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleProcessClick = () => {
    if (selectedFile) {
      onProcessFile(selectedFile);
    }
  };

  return (
    <section className="mb-8">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="audio/*"
            className="hidden"
          />
          <button
            onClick={handleUploadClick}
            className="w-full bg-white hover:bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200 transition-all duration-200 flex flex-col items-center text-center group"
          >
            <div className="h-12 w-12 bg-indigo-100 rounded-full flex items-center justify-center mb-3 text-indigo-600 group-hover:bg-indigo-200 transition-colors">
              <UploadCloud className="h-6 w-6" />
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Upload New Demo</h3>
            <p className="text-sm text-gray-500">From recording file</p>
          </button>
          {selectedFile && (
            <div className="mt-2 text-sm text-gray-700 text-center">
              Selected file: {selectedFile.name}
            </div>
          )}
          <button
            onClick={handleProcessClick}
            disabled={!selectedFile}
            className={`mt-2 w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg shadow-sm transition-all duration-200 ${!selectedFile ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            Process the File
          </button>
        </div>

        <button
          className="bg-white hover:bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200 transition-all duration-200 flex flex-col items-center text-center group"
        >
          <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center mb-3 text-green-600 group-hover:bg-green-200 transition-colors">
            <PlusCircle className="h-6 w-6" />
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Connect Meeting Platform</h3>
          <p className="text-sm text-gray-500">Zoom, Meet, Teams integration</p>
        </button>

        <button
          className="bg-white hover:bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200 transition-all duration-200 flex flex-col items-center text-center group"
        >
          <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center mb-3 text-blue-600 group-hover:bg-blue-200 transition-colors">
            <ExternalLink className="h-6 w-6" />
          </div>
          <h3 className="font-medium text-gray-900 mb-1">View Microsite Analytics</h3>
          <p className="text-sm text-gray-500">Engagement & performance</p>
        </button>
      </div>
    </section>
  );
};

export default QuickActions;