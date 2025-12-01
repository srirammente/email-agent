import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DraftEditor from './DraftEditor';
import { API_BASE_URL } from '../config';

const EmailDetail = () => {
    const { emailId } = useParams(); // Get emailId from URL
    const navigate = useNavigate();
    const [email, setEmail] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [showDraft, setShowDraft] = useState(false);

    useEffect(() => {
        if (emailId) {
            console.log('EmailDetail: Fetching email for ID:', emailId);
            fetchEmailDetail();
        } else {
            console.log('EmailDetail: No emailId found in URL parameters.');
        }
    }, [emailId]);

    const fetchEmailDetail = async () => {
        try {
            const url = `${API_BASE_URL}/emails/${emailId}`;
            console.log('EmailDetail: Fetching from URL:', url);
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('EmailDetail: Received data:', data);
            setEmail(data);
        } catch (error) {
            console.error('EmailDetail: Error fetching email detail:', error);
            navigate('/inbox'); // Navigate back to inbox on error
        }
    };

    if (!email) {
        return <div className="card">Loading email...</div>;
    }

    const processEmail = async () => {
        setProcessing(true);
        try {
            await fetch(`${API_BASE_URL}/emails/${email.id}/process`, {
                method: 'POST'
            });
            fetchEmailDetail();
            setProcessing(false);
        } catch (error) {
            console.error('EmailDetail: Error processing email:', error);
            setProcessing(false);
        }
    };

    if (showDraft) {
        return <DraftEditor email={email} onBack={() => setShowDraft(false)} />;
    }

    return (
        <div className="card">
            <div className="card-header">
                <button className="btn btn-secondary" onClick={() => navigate(-1)}>← Back</button>
                <div className="email-detail-actions">
                    <button className="btn btn-secondary" onClick={processEmail} disabled={processing}>
                        {processing ? 'Processing...' : '✨ Analyze with AI'}
                    </button>
                    <button className="btn btn-secondary" onClick={() => navigate(`/agent?emailId=${emailId}`)}>
                        💬 Chat about this email
                    </button>
                    <button className="btn btn-primary" onClick={() => setShowDraft(true)}>Reply</button>
                </div>
            </div>

            <div className="email-content-section">
                <h1 className="email-subject">{email.subject}</h1>
                <div className="email-meta-detail">
                    From: {email.sender} • {new Date(email.timestamp).toLocaleString()}
                </div>

                <div className="email-body-content">
                    {email.body}
                </div>
            </div>

            {(email.category || email.action_items || email.summary) && (
                <div className="ai-analysis-card">
                    <h3>AI Analysis</h3>

                    {email.category && (
                        <div className="ai-analysis-item">
                            <strong>Category: </strong>
                            <span className={`badge ${email.category.toLowerCase()}`}>{email.category}</span>
                        </div>
                    )}

                    {email.summary && (
                        <div className="ai-analysis-item">
                            <strong>Summary: </strong>
                            <span>{email.summary}</span>
                        </div>
                    )}

                    {email.action_items && email.action_items.length > 0 && (
                        <div className="ai-analysis-item">
                            <strong>Action Items:</strong>
                            <ul className="ai-analysis-list">
                                {email.action_items.map((item, idx) => (
                                    <li key={idx}>
                                        {typeof item === 'object' ? (
                                            <>
                                                <strong>{item.task}</strong>
                                                {item.deadline && <span className="text-secondary"> (By: {item.deadline})</span>}
                                            </>
                                        ) : (
                                            item
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default EmailDetail;
