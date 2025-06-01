import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { GoogleOAuthProvider, CredentialResponse } from '@react-oauth/google';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import LandingPage from './components/LandingPage.tsx';

const clientId = '697057348677-6dlr90s451midhbkd3s96g8j0rq75r5c.apps.googleusercontent.com'; // Your Google Client ID

// Component to handle authentication state and routing
const AppRouter = () => {
  const [user, setUser] = useState<any>(null); // State to hold authenticated user info
  const navigate = useNavigate(); // Get the navigate function

  // Effect to handle redirection after user state updates
  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]); // Rerun effect when user or navigate changes

  // Function to handle successful authentication and set user state
  const handleAuthSuccess = (credentialResponse: CredentialResponse) => {
    console.log('Auth Success in AppRouter:', credentialResponse);
    // In a real app, you would verify the credentialResponse.credential server-side
    // and get trusted user data. For this example, we'll decode the ID token
    try {
      const idToken = credentialResponse.credential;
      if (idToken) {
        const payload = JSON.parse(atob(idToken.split('.')[1]));
        console.log('ID Token Payload:', payload);
        const userName = payload.name || payload.email || 'Authenticated User';
         // Store user data in localStorage or a more persistent state management for reloads
        localStorage.setItem('user', JSON.stringify({ name: userName }));
        setUser({ name: userName }); // Set user state
      } else {
        console.error('No ID token in credential response');
        // Handle error
      }
    } catch (error) {
      console.error('Error decoding ID token:', error);
      // Handle error
    }
  };

  // Check for user in localStorage on initial load
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []); // Run only on mount


  return (
    <Routes>
      {/* Pass handleAuthSuccess to LandingPage */}
      <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <LandingPage onAuthSuccess={handleAuthSuccess} />} />

      {/* Pass user info to App. Basic protection: redirect to login if no user */}
      <Route
        path="/dashboard"
        element={user ? <App user={user} /> : <Navigate to="/" replace />}
      />

      {/* Redirect any other unknown routes to the landing page if not authenticated */}
       <Route path="*" element={user ? <Navigate to="/dashboard" replace /> : <Navigate to="/" replace />} />
    </Routes>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={clientId}>
      <Router> {/* Router wraps AppRouter */}
        <AppRouter />
      </Router>
    </GoogleOAuthProvider>
  </React.StrictMode>,
)
