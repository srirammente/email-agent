import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';

const PromptBrain = () => {
    const [prompts, setPrompts] = useState({
        categorization: '',
        action_item: '',
        auto_reply: ''
    });
    const [saving, setSaving] = useState(false);
    const [activeTab, setActiveTab] = useState('categorization'); // New state for active tab

    useEffect(() => {
        fetchPrompts();
    }, []);

    const fetchPrompts = async () => {
        const res = await fetch(`${API_BASE_URL}/prompts`);
        const data = await res.json();
        setPrompts(data);
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            await fetch(`${API_BASE_URL}/prompts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(prompts)
            });
            setSaving(false);
            alert('Prompts saved successfully!'); // Consider a more subtle feedback
        } catch (e) {
            console.error(e);
            setSaving(false);
        }
    };

    const renderPromptContent = () => {
        switch (activeTab) {
            case 'categorization':
                return (
                    <textarea
                        rows={8}
                        value={prompts.categorization}
                        onChange={(e) => setPrompts({ ...prompts, categorization: e.target.value })}
                        placeholder="Instructions for categorizing emails..."
                    />
                );
            case 'action_item':
                return (
                    <textarea
                        rows={8}
                        value={prompts.action_item}
                        onChange={(e) => setPrompts({ ...prompts, action_item: e.target.value })}
                        placeholder="Instructions for extracting tasks..."
                    />
                );
            case 'auto_reply':
                return (
                    <textarea
                        rows={8}
                        value={prompts.auto_reply}
                        onChange={(e) => setPrompts({ ...prompts, auto_reply: e.target.value })}
                        placeholder="Instructions for drafting replies..."
                    />
                );
            default:
                return null;
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <h2 className="card-title">Agent Brain Configuration</h2>
                <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                    {saving ? 'Saving...' : 'Save Configuration'}
                </button>
            </div>

            <div className="tab-navigation">
                <button
                    className={`tab-btn ${activeTab === 'categorization' ? 'active' : ''}`}
                    onClick={() => setActiveTab('categorization')}
                >
                    Categorization
                </button>
                <button
                    className={`tab-btn ${activeTab === 'action_item' ? 'active' : ''}`}
                    onClick={() => setActiveTab('action_item')}
                >
                    Action Items
                </button>
                <button
                    className={`tab-btn ${activeTab === 'auto_reply' ? 'active' : ''}`}
                    onClick={() => setActiveTab('auto_reply')}
                >
                    Auto-Reply
                </button>
            </div>

            <div className="prompt-content">
                {renderPromptContent()}
            </div>
        </div>
    );
};

export default PromptBrain;
