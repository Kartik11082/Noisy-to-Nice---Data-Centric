import { useState, useEffect } from 'react';
import Auth from './components/Auth';
import FileUpload from './components/FileUpload';
import api from './services/api';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [username, setUsername] = useState('');

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('token');
        if (token) {
            const result = api.verify_token ? api.verify_token(token) : null;
            // For now, just check if token exists
            setIsAuthenticated(true);
        }
    }, []);

    const handleLogin = (user) => {
        setUsername(user);
        setIsAuthenticated(true);
    };

    const handleLogout = () => {
        api.clearToken();
        setUsername('');
        setIsAuthenticated(false);
    };

    return (
        <>
            {isAuthenticated ? (
                <FileUpload username={username} onLogout={handleLogout} />
            ) : (
                <Auth onLogin={handleLogin} />
            )}
        </>
    );
}

export default App;
