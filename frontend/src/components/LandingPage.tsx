import React from 'react';
import { GoogleOAuthProvider, GoogleLogin, CredentialResponse } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';

interface LandingPageProps {
  onAuthSuccess: (userData: CredentialResponse) => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onAuthSuccess }) => {
  const navigate = useNavigate();

  const handleGoogleSuccess = (credentialResponse: CredentialResponse) => {
    console.log('Google Auth Success:', credentialResponse);
    // TODO: Send credentialResponse.credential to your backend for verification if needed
    // For this example, we'll just simulate successful auth and pass the credentialResponse
    onAuthSuccess(credentialResponse); // Pass the credentialResponse to the prop
    // navigate('/dashboard'); // Navigation is now handled in AppRouter after state update
  };

  const handleGoogleError = () => {
    console.log('Login Failed');
    // Handle login failure (e.g., show an error message)
    alert('Google Sign-in failed. Please try again.');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-yellow-300 p-4">
      <div className="bg-white border-4 border-black rounded-lg shadow-[8px_8px_0px_rgba(0,0,0,1)] p-8 w-full max-w-md text-center">
        <h1 className="text-4xl font-bold text-black mb-4 font-mono">Microsite Generator</h1>
        <p className="text-black mb-8 font-sans">Your tool to convert audio to amazing microsites.</p>
        
        <div className="flex justify-center">
           {/* Google Sign-in Button will be rendered here by GoogleLogin component */}
           <GoogleLogin
             onSuccess={handleGoogleSuccess}
             onError={handleGoogleError}
           />
        </div>
      </div>
    </div>
  );
};

export default LandingPage; 