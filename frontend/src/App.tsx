import React, { useState } from 'react';
import Header from './components/Header';
import QuickActions from './components/QuickActions';
import DemoList from './components/DemoList';
import { initialDemos } from './data/mockData';
import { Demo, ActionType } from './types';
import { v4 as uuidv4 } from './utils/uuid';

interface AppProps {
  user: { name: string } | null; // Define the expected user prop
}

function App({ user }: AppProps) { // Accept the user prop
  const [demos, setDemos] = useState<Demo[]>(initialDemos);

  const handleProcessFile = async (file: File) => {
    const newDemoId = uuidv4();
    const newDemo: Demo = {
      id: newDemoId,
      title: file.name,
      date: new Date().toISOString().split('T')[0],
      salesRep: 'Jane Doe',
      status: 'Processing' as const,
      micrositeUrl: undefined,
    };

    setDemos(prevDemos => [newDemo, ...prevDemos]);

    const apiUrl = 'https://micrositegenerator.onrender.com/transcribe';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Parse the JSON response
      const result = await response.json(); // Use .json() to parse JSON
      console.log('API Response:', result);

      // Check if the API call was successful and deployment details are present
      if (result.status === 'success' && result.deployment?.site?.url) {
        const deployedUrl = result.deployment.site.url;

        setDemos(prevDemos =>
          prevDemos.map(demo =>
            demo.id === newDemoId
              ? {
                  ...demo,
                  status: 'Ready' as const,
                  micrositeUrl: deployedUrl, // Use the actual deployed URL
                   // Optional: Update title from response if available and suitable
                  title: result.deployment?.site?.name || demo.title, 
                }
              : demo
          )
        );
      } else {
        // Handle cases where API call was successful but deployment failed or URL is missing
        console.error('API response indicates failure or missing URL:', result);
         setDemos(prevDemos =>
          prevDemos.map(demo =>
            demo.id === newDemoId
              ? { ...demo, status: 'Failed' as const }
              : demo
          )
        );
        alert('Processing completed, but microsite URL not available.');
      }

    } catch (error) {
      console.error('Error processing file:', error);
      setDemos(prevDemos =>
        prevDemos.map(demo =>
          demo.id === newDemoId
            ? { ...demo, status: 'Failed' as const }
            : demo
        )
      );
      alert('Error processing file. Check console for details.');
    }
  };

  const handleAction = (type: ActionType, demo: Demo) => {
    switch (type) {
      case 'view':
        if (demo.micrositeUrl) {
          alert(`Viewing microsite: ${demo.micrositeUrl}`);
        }
        break;
      case 'share':
        if (demo.micrositeUrl) {
          alert(`Sharing microsite: ${demo.micrositeUrl}`);
        }
        break;
      case 'regenerate':
        alert(`Regenerating microsite for: ${demo.title}`);
        // Mock regeneration by setting status to Processing
        setDemos(prevDemos => 
          prevDemos.map(d => 
            d.id === demo.id ? { ...d, status: 'Processing' as const } : d
          )
        );
        // Simulate completion after 3 seconds
        setTimeout(() => {
          setDemos(prevDemos => 
            prevDemos.map(d => 
              d.id === demo.id ? { 
                ...d, 
                status: 'Ready' as const,
                micrositeUrl: `https://microsite.example.com/${demo.title.toLowerCase().replace(/\s+/g, '-')}` 
              } : d
            )
          );
        }, 3000);
        break;
      case 'delete':
        if (confirm(`Are you sure you want to delete "${demo.title}"?`)) {
          setDemos(prevDemos => prevDemos.filter(d => d.id !== demo.id));
        }
        break;
      case 'upload':
        handleUploadDemo();
        break;
      default:
        break;
    }
  };

  const handleUploadDemo = () => {
    const newDemo: Demo = {
      id: uuidv4(),
      title: `New Demo ${new Date().toLocaleTimeString()}`,
      date: new Date().toISOString().split('T')[0],
      salesRep: 'Jane Doe',
      status: 'Processing'
    };
    
    setDemos(prevDemos => [newDemo, ...prevDemos]);
    
    // Simulate processing completion after 5 seconds
    setTimeout(() => {
      setDemos(prevDemos => 
        prevDemos.map(d => 
          d.id === newDemo.id ? { 
            ...d, 
            status: 'Ready' as const,
            micrositeUrl: `https://microsite.example.com/${newDemo.title.toLowerCase().replace(/\s+/g, '-')}` 
          } : d
        )
      );
    }, 5000);
  };

  return (
    <div className="min-h-screen bg-gray-50 font-['Inter']">
      <Header userName={user?.name} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <QuickActions onUploadDemo={handleUploadDemo} onProcessFile={handleProcessFile} />
        <DemoList demos={demos} onAction={handleAction} />
      </main>
    </div>
  );
}

export default App;