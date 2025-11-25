import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { API_BASE_URL } from '../config';

const Inbox = () => {
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchEmails();
    }, []);

    const fetchEmails = async () => {
        console.log('Attempting to fetch emails...');
        try {
            const response = await fetch(`${API_BASE_URL}/emails`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Emails fetched successfully:', data);
            setEmails(data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching emails:', error);
            setLoading(false);
        }
    };

    const loadMockEmails = async () => {
        setLoading(true);
        console.log('Attempting to load mock emails...');
        try {
            const response = await fetch(`${API_BASE_URL}/emails/load-mock`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            console.log('Mock emails loaded successfully.');
            await fetchEmails();
        } catch (error) {
            console.error('Error loading mock emails:', error);
            alert('Failed to load emails. Check console/backend logs.');
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <h2 className="card-title">Inbox ({emails.length})</h2>
                <div className="btn-group"> {/* Applied new class */}
                    <button className="btn btn-secondary" onClick={loadMockEmails}>📧 Load Emails</button>
                    <button className="btn btn-secondary" onClick={fetchEmails}>Refresh</button>
                </div>
            </div>

            {loading ? (
                <div>Loading emails...</div>
            ) : (
                <div className="email-list">
                    {emails.map((email) => (
                        <div
                            key={email.id}
                            className={`email-item ${!email.read ? 'unread' : ''}`}
                            onClick={() => {
                                console.log('Navigating to email:', email.id);
                                navigate(`/inbox/${email.id}`);
                            }}
                        >
                            <div className="email-meta">
                                <span>{email.sender}</span>
                                <span>{new Date(email.timestamp).toLocaleDateString()}</span>
                            </div>
                            <div className="subject">{email.subject}</div>
                            <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                                {email.category && (
                                    <span className={`badge ${email.category.toLowerCase()}`}>
                                        {email.category}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Inbox;
