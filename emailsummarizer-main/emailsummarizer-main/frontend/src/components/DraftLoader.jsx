import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DraftEditor from './DraftEditor';

import { API_BASE_URL } from '../config';

const DraftLoader = () => {
    const { draftId } = useParams();
    const navigate = useNavigate();
    const [draft, setDraft] = useState(null);
    const [email, setEmail] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                console.log('DraftLoader: Loading draft ID:', draftId);

                // 1. Fetch Draft directly
                const draftRes = await fetch(`${API_BASE_URL}/drafts/${draftId}`);

                if (!draftRes.ok) {
                    throw new Error(`Failed to fetch draft: ${draftRes.status}`);
                }

                const foundDraft = await draftRes.json();
                console.log('DraftLoader: Loaded draft:', foundDraft);
                setDraft(foundDraft);

                // 2. Fetch Email
                if (foundDraft.email_id) {
                    console.log('DraftLoader: Loading email ID:', foundDraft.email_id);
                    const emailRes = await fetch(`${API_BASE_URL}/emails/${foundDraft.email_id}`);
                    if (emailRes.ok) {
                        const emailData = await emailRes.json();
                        console.log('DraftLoader: Loaded email:', emailData);
                        setEmail(emailData);
                    } else {
                        console.warn('DraftLoader: Email not found, continuing without it');
                    }
                }
            } catch (e) {
                console.error("DraftLoader: Error loading draft:", e);
                alert(`Error loading draft: ${e.message}`);
                navigate('/drafts');
            }
            setLoading(false);
        };

        loadData();
    }, [draftId, navigate]);

    if (loading) return <div>Loading draft...</div>;
    if (!draft) return <div>Draft not found.</div>;

    return (
        <DraftEditor
            initialDraft={draft}
            email={email}
            onBack={() => navigate('/drafts')}
        />
    );
};

export default DraftLoader;
