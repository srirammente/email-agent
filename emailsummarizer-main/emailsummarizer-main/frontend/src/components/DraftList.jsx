import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';

const DraftList = ({ onSelectDraft }) => {
    const [drafts, setDrafts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDrafts();
    }, []);

    const fetchDrafts = async () => {
        try {
            console.log('DraftList: Fetching drafts...');
            const res = await fetch(`${API_BASE_URL}/drafts`);

            if (!res.ok) {
                throw new Error(`Failed to fetch drafts: ${res.status}`);
            }

            const data = await res.json();
            console.log('DraftList: Loaded drafts:', data);

            // Fetch email details for each draft to get the original email subject
            const draftsWithEmails = await Promise.all(
                data.map(async (draft) => {
                    if (draft.email_id) {
                        try {
                            const emailRes = await fetch(`${API_BASE_URL}/emails/${draft.email_id}`);
                            if (emailRes.ok) {
                                const emailData = await emailRes.json();
                                return { ...draft, originalEmail: emailData };
                            }
                        } catch (e) {
                            console.warn(`Could not fetch email ${draft.email_id}:`, e);
                        }
                    }
                    return draft;
                })
            );

            setDrafts(draftsWithEmails);
        } catch (e) {
            console.error("DraftList: Error fetching drafts:", e);
            setError(e.message);
        }
        setLoading(false);
    };

    if (loading) return <div className="card"><div className="p-4">Loading drafts...</div></div>;
    if (error) return <div className="card"><div className="p-4 text-danger">Error: {error}</div></div>;

    return (
        <div className="card">
            <div className="card-header">
                <h2 className="card-title">Saved Drafts</h2>
            </div>
            <div className="email-list">
                {drafts.length === 0 ? (
                    <div className="p-4 text-secondary">No saved drafts found.</div>
                ) : (
                    drafts.map(draft => (
                        <div key={draft.id} className="draft-item" onClick={() => onSelectDraft(draft)}>
                            <div className="draft-item-header">
                                <div className="draft-original-info">
                                    <span className="draft-label">Replying to:</span>
                                    {draft.originalEmail ? (
                                        <>
                                            <span className="draft-sender">{draft.originalEmail.sender}</span>
                                            <span className="draft-original-subject">{draft.originalEmail.subject}</span>
                                        </>
                                    ) : (
                                        <span className="draft-sender">Email ID {draft.email_id}</span>
                                    )}
                                </div>
                                <span className="draft-date">{new Date(draft.created_at).toLocaleDateString()}</span>
                            </div>
                            <div className="draft-subject-line">
                                <span className="draft-label">Your Draft:</span>
                                <span className="draft-subject">{draft.subject}</span>
                            </div>
                            <div className="draft-preview">{draft.body.substring(0, 120)}...</div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default DraftList;
