import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import Auth from './components/Auth';
import FileUpload from './components/FileUpload';
import DataQuality from './components/DataQuality';
import api from './services/api';

// Analysis page wrapper
function AnalysisPage() {
    const { fileId } = useParams();
    return <DataQuality fileId={fileId} />;
}

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [username, setUsername] = useState('');

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('token');
        if (token) {
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

    if (!isAuthenticated) {
        return <Auth onLogin={handleLogin} />;
    }

    return (
        <Router>
            <Routes>
                <Route path="/" element={<FileUpload username={username} onLogout={handleLogout} />} />
                <Route path="/analysis/:fileId" element={<AnalysisPage />} />
            </Routes>
        </Router>
    );
}

export default App;
