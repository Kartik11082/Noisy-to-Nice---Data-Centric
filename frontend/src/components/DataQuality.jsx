import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './DataQuality.css';

export default function DataQuality({ fileId }) {
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);
    const [analyzing, setAnalyzing] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        loadAnalysis();
    }, [fileId]);

    const loadAnalysis = async () => {
        setLoading(true);
        const result = await api.getAnalysis(fileId);

        if (result.success) {
            setAnalysis(result);
        } else if (result.status === 'not_started') {
            // No analysis yet
            setAnalysis(null);
        }
        setLoading(false);
    };

    const handleAnalyze = async () => {
        setAnalyzing(true);
        setError('');

        const result = await api.analyzeFile(fileId);

        if (result.success) {
            // Reload analysis
            await loadAnalysis();
        } else {
            setError(result.message || 'Analysis failed');
        }

        setAnalyzing(false);
    };

    const getScoreColor = (score) => {
        if (score >= 80) return 'var(--color-success)';
        if (score >= 60) return 'var(--color-warning)';
        return 'var(--color-error)';
    };

    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'critical':
                return '🔴';
            case 'warning':
                return '⚠️';
            default:
                return 'ℹ️';
        }
    };

    if (loading) {
        return (
            <div className="quality-container">
                <div className="loading-container">
                    <div className="spinner" style={{ width: '40px', height: '40px' }}></div>
                    <p>Loading analysis...</p>
                </div>
            </div>
        );
    }

    if (!analysis) {
        return (
            <div className="quality-container">
                <div className="no-analysis card">
                    <h2>No Analysis Available</h2>
                    <p>Generate a data quality report to get AI-powered insights</p>
                    {error && <div className="alert alert-error">{error}</div>}
                    <button
                        onClick={handleAnalyze}
                        className="btn btn-primary"
                        disabled={analyzing}
                    >
                        {analyzing ? (
                            <>
                                <span className="spinner"></span>
                                Analyzing...
                            </>
                        ) : 'Analyze Dataset'}
                    </button>
                    <button onClick={() => navigate('/')} className="btn btn-secondary">
                        Back to Files
                    </button>
                </div>
            </div>
        );
    }

    const { quality_score, metrics, issues, ai_insights } = analysis;

    return (
        <div className="quality-container">
            <div className="quality-header">
                <div>
                    <h1>{analysis.filename}</h1>
                    <button onClick={() => navigate('/')} className="btn btn-secondary btn-sm">
                        ← Back to Files
                    </button>
                </div>
                <a
                    href={analysis.profiling_report_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary"
                >
                    View Full Report
                </a>
            </div>

            {/* Quality Score */}
            <div className="score-section card fade-in">
                <h2>Data Quality Score</h2>
                <div className="score-display">
                    <div
                        className="score-circle"
                        style={{
                            background: `conic-gradient(${getScoreColor(quality_score)} ${quality_score}%, var(--color-bg-tertiary) 0)`
                        }}
                    >
                        <div className="score-inner">
                            <span className="score-value">{quality_score}</span>
                            <span className="score-max">/100</span>
                        </div>
                    </div>
                    <div className="score-label">
                        {quality_score >= 80 && 'Excellent Quality'}
                        {quality_score >= 60 && quality_score < 80 && 'Good Quality'}
                        {quality_score < 60 && 'Needs Improvement'}
                    </div>
                </div>
            </div>

            {/* Metrics */}
            <div className="metrics-grid">
                <div className="metric-card card fade-in">
                    <div className="metric-icon">📊</div>
                    <div className="metric-info">
                        <div className="metric-value">{metrics.total_rows?.toLocaleString()}</div>
                        <div className="metric-label">Total Rows</div>
                    </div>
                </div>

                <div className="metric-card card fade-in">
                    <div className="metric-icon">📋</div>
                    <div className="metric-info">
                        <div className="metric-value">{metrics.total_columns}</div>
                        <div className="metric-label">Total Columns</div>
                    </div>
                </div>

                <div className="metric-card card fade-in">
                    <div className="metric-icon">❌</div>
                    <div className="metric-info">
                        <div className="metric-value">{metrics.missing_percentage}%</div>
                        <div className="metric-label">Missing Data</div>
                    </div>
                </div>

                <div className="metric-card card fade-in">
                    <div className="metric-icon">🔄</div>
                    <div className="metric-info">
                        <div className="metric-value">{metrics.duplicate_rows?.toLocaleString()}</div>
                        <div className="metric-label">Duplicates</div>
                    </div>
                </div>
            </div>

            {/* Issues */}
            {issues && issues.length > 0 && (
                <div className="issues-section card fade-in">
                    <h2>Issues Found</h2>
                    <div className="issues-list">
                        {issues.map((issue, index) => (
                            <div key={index} className={`issue-item severity-${issue.severity}`}>
                                <div className="issue-header">
                                    <span className="issue-icon">{getSeverityIcon(issue.severity)}</span>
                                    <span className="issue-type">{issue.type.replace('_', ' ')}</span>
                                    <span className={`issue-badge badge-${issue.severity}`}>{issue.severity}</span>
                                </div>
                                <div className="issue-message">{issue.message}</div>
                                <div className="issue-suggestion">💡 {issue.suggestion}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* AI Insights */}
            {ai_insights && (
                <div className="ai-section card fade-in">
                    <div className="ai-header">
                        <h2>AI-Powered Insights</h2>
                        <span className="ai-badge">✨ Powered by AWS Bedrock</span>
                    </div>

                    <div className="ai-assessment">
                        <h3>Assessment</h3>
                        <p>{ai_insights.assessment}</p>
                    </div>

                    {ai_insights.recommendations && ai_insights.recommendations.length > 0 && (
                        <div className="ai-recommendations">
                            <h3>Recommendations</h3>
                            <ol className="recommendations-list">
                                {ai_insights.recommendations.map((rec, index) => (
                                    <li key={index}>{rec}</li>
                                ))}
                            </ol>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
