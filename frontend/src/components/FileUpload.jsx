import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './FileUpload.css';

export default function FileUpload({ username, onLogout }) {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });
    const navigate = useNavigate();

    useEffect(() => {
        loadFiles();
    }, []);

    const loadFiles = async () => {
        setLoading(true);
        const result = await api.getFiles();
        if (result.success) {
            setFiles(result.files || []);
        }
        setLoading(false);
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    };

    const handleFileSelect = (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFileUpload(e.target.files[0]);
        }
    };

    const handleFileUpload = async (file) => {
        if (!file.name.toLowerCase().endsWith('.csv')) {
            setMessage({ type: 'error', text: 'Only CSV files are allowed' });
            return;
        }

        setMessage({ type: '', text: '' });
        setUploading(true);

        try {
            const result = await api.uploadFile(file);

            if (result.success) {
                setMessage({ type: 'success', text: 'File uploaded successfully!' });
                loadFiles();
                setTimeout(() => setMessage({ type: '', text: '' }), 3000);
            } else {
                setMessage({ type: 'error', text: result.message || 'Upload failed' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'An error occurred during upload' });
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (fileId) => {
        if (!confirm('Are you sure you want to delete this file?')) return;

        const result = await api.deleteFile(fileId);
        if (result.success) {
            setMessage({ type: 'success', text: 'File deleted successfully' });
            loadFiles();
            setTimeout(() => setMessage({ type: '', text: '' }), 3000);
        } else {
            setMessage({ type: 'error', text: 'Failed to delete file' });
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    };

    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleString();
    };

    return (
        <div className="upload-container container">
            <header className="upload-header">
                <div>
                    <h1 className="upload-title">ML Dataset Uploader</h1>
                    <p className="upload-subtitle">Welcome, <span className="username-highlight">{username}</span></p>
                </div>
                <button onClick={onLogout} className="btn btn-secondary">
                    Logout
                </button>
            </header>

            {message.text && (
                <div className={`alert alert-${message.type} fade-in`}>
                    {message.text}
                </div>
            )}

            <div className="upload-section card fade-in">
                <h2 className="section-title">Upload Dataset</h2>

                <div
                    className={`dropzone ${dragActive ? 'active' : ''} ${uploading ? 'uploading' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        id="file-input"
                        className="file-input"
                        accept=".csv"
                        onChange={handleFileSelect}
                        disabled={uploading}
                    />

                    {uploading ? (
                        <div className="dropzone-content">
                            <div className="spinner" style={{ width: '40px', height: '40px' }}></div>
                            <p className="dropzone-text">Uploading...</p>
                        </div>
                    ) : (
                        <label htmlFor="file-input" className="dropzone-content">
                            <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <p className="dropzone-text">
                                <span className="dropzone-highlight">Click to upload</span> or drag and drop
                            </p>
                            <p className="dropzone-hint">CSV files only</p>
                        </label>
                    )}
                </div>
            </div>

            <div className="files-section">
                <h2 className="section-title">Your Datasets</h2>

                {loading ? (
                    <div className="loading-container">
                        <div className="spinner" style={{ width: '40px', height: '40px' }}></div>
                        <p className="loading-text">Loading files...</p>
                    </div>
                ) : files.length === 0 ? (
                    <div className="empty-state card">
                        <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                        </svg>
                        <p className="empty-text">No datasets uploaded yet</p>
                        <p className="empty-hint">Upload your first CSV file to get started</p>
                    </div>
                ) : (
                    <div className="files-grid">
                        {files.map((file, index) => (
                            <div key={file.file_id} className="file-card card fade-in" style={{ animationDelay: `${index * 50}ms` }}>
                                <div className="file-header">
                                    <svg className="file-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    <div className="file-info">
                                        <h3 className="file-name">{file.filename}</h3>
                                        <p className="file-date">{formatDate(file.upload_timestamp)}</p>
                                    </div>
                                </div>

                                <div className="file-metadata">
                                    <div className="metadata-item">
                                        <span className="metadata-label">Size</span>
                                        <span className="metadata-value">{formatFileSize(file.file_size)}</span>
                                    </div>

                                    {file.row_count !== undefined && (
                                        <div className="metadata-item">
                                            <span className="metadata-label">Rows</span>
                                            <span className="metadata-value">{file.row_count.toLocaleString()}</span>
                                        </div>
                                    )}

                                    {file.column_count !== undefined && (
                                        <div className="metadata-item">
                                            <span className="metadata-label">Columns</span>
                                            <span className="metadata-value">{file.column_count}</span>
                                        </div>
                                    )}
                                </div>

                                {file.columns && file.columns.length > 0 && (
                                    <div className="file-columns">
                                        <p className="columns-label">Columns:</p>
                                        <div className="columns-list">
                                            {file.columns.slice(0, 5).map((col, i) => (
                                                <span key={i} className="column-tag">{col}</span>
                                            ))}
                                            {file.columns.length > 5 && (
                                                <span className="column-tag more">+{file.columns.length - 5} more</span>
                                            )}
                                        </div>
                                    </div>
                                )}

                                <div className="file-actions">
                                    <button
                                        onClick={() => navigate(`/analysis/${file.file_id}`)}
                                        className="btn btn-primary btn-sm"
                                    >
                                        📊 Analyze Quality
                                    </button>
                                    <a
                                        href={file.s3_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn-secondary btn-sm"
                                    >
                                        View in S3
                                    </a>
                                    <button
                                        onClick={() => handleDelete(file.file_id)}
                                        className="btn btn-danger btn-sm"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
