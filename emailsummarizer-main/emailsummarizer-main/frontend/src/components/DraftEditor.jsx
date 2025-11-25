import React, { useState } from 'react';
import { API_BASE_URL } from '../config';

const DraftEditor = ({ email, initialDraft, onBack }) => {
    const [instructions, setInstructions] = useState('');
    const [draft, setDraft] = useState(initialDraft || null);
    const [generating, setGenerating] = useState(false);
    const [toast, setToast] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);

    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    };

    const generateDraft = async () => {
        setGenerating(true);
        try {
            const res = await fetch(`${API_BASE_URL}/drafts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_id: email ? email.id : (initialDraft ? initialDraft.email_id : null),
                    instructions: instructions || "Reply to this email"
                })
            });
            const data = await res.json();
            setDraft(data);
            showToast('Draft generated successfully!');
        } catch (e) {
            console.error(e);
            showToast('Error generating draft', 'error');
        }
        setGenerating(false);
    };

    const saveDraft = async () => {
        if (!draft || !draft.id) {
            showToast('No draft to save. Please generate one first.', 'error');
            return;
        }
        try {
            const res = await fetch(`${API_BASE_URL}/drafts/${draft.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subject: draft.subject,
                    body: draft.body,
                    suggested_follow_ups: draft.suggested_follow_ups,
                    draft_metadata: draft.metadata
                })
            });
            if (res.ok) {
                showToast('Draft saved successfully!');
            } else {
                showToast('Failed to save draft', 'error');
            }
        } catch (e) {
            console.error(e);
            showToast('Error saving draft', 'error');
        }
    };

    const confirmDelete = async () => {
        setShowDeleteModal(false);
        try {
            const res = await fetch(`${API_BASE_URL}/drafts/${draft.id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                showToast('Draft deleted successfully!');
                setTimeout(() => onBack(), 1500);
            } else {
                showToast('Failed to delete draft', 'error');
            }
        } catch (e) {
            console.error(e);
            showToast('Error deleting draft', 'error');
        }
    };

    return (
        <div className="card">
            {/* Toast Notification */}
            {toast && (
                <div className={`toast toast-${toast.type}`}>
                    {toast.message}
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {showDeleteModal && (
                <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>Delete Draft?</h3>
                        <p>Are you sure you want to delete this draft? This action cannot be undone.</p>
                        <div className="modal-actions">
                            <button className="btn btn-secondary" onClick={() => setShowDeleteModal(false)}>Cancel</button>
                            <button className="btn btn-danger" onClick={confirmDelete}>Delete</button>
                        </div>
                    </div>
                </div>
            )}

            <div className="card-header">
                <h2 className="card-title">Draft Reply</h2>
                <div style={{ flexGrow: 1 }}></div>
                <button className="btn btn-secondary" onClick={onBack}>Cancel</button>
            </div>

            <div className="draft-editor-grid">
                <div className="draft-section">
                    <h3>Instructions</h3>
                    <p className="text-secondary">
                        Tell the agent how to reply (e.g., "Polite refusal", "Ask for more time").
                    </p>
                    <textarea
                        rows={4}
                        value={instructions}
                        onChange={(e) => setInstructions(e.target.value)}
                        placeholder="Enter instructions..."
                    />
                    <button className="btn-generate" onClick={generateDraft} disabled={generating}>
                        {generating ? 'Generating...' : 'Generate Draft'}
                    </button>

                    <div className="original-email-context">
                        <strong>Original Email Context:</strong>
                        <p>{email ? email.body.substring(0, 200) + '...' : 'Original email content not available.'}</p>
                    </div>
                </div>

                <div className="draft-section">
                    <h3>Draft Preview</h3>
                    {draft ? (
                        <div className="draft-output-section">
                            <input
                                type="text"
                                value={draft.subject}
                                onChange={(e) => setDraft({ ...draft, subject: e.target.value })}
                            />
                            <textarea
                                rows={15}
                                value={draft.body}
                                onChange={(e) => setDraft({ ...draft, body: e.target.value })}
                            />

                            {/* Suggested Follow-ups Section */}
                            {draft.suggested_follow_ups && draft.suggested_follow_ups.length > 0 && (
                                <div className="draft-metadata-section">
                                    <strong>💡 Suggested Follow-ups:</strong>
                                    <ul>
                                        {draft.suggested_follow_ups.map((item, idx) => (
                                            <li key={idx}>{item}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Metadata Section */}
                            {draft.metadata && Object.keys(draft.metadata).length > 0 && (
                                <div className="draft-metadata-section">
                                    <strong>📋 Draft Metadata:</strong>
                                    <div className="metadata-content">
                                        {draft.metadata.category && (
                                            <div><strong>Category:</strong> {draft.metadata.category}</div>
                                        )}
                                        {draft.metadata.action_items && draft.metadata.action_items.length > 0 && (
                                            <div>
                                                <strong>Action Items:</strong>
                                                <ul>
                                                    {draft.metadata.action_items.map((item, idx) => (
                                                        <li key={idx}>
                                                            {item.task} {item.deadline && `(By: ${item.deadline})`}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            <div className="draft-actions">
                                <button className="btn btn-danger" onClick={() => setShowDeleteModal(true)}>Delete Draft</button>
                                <button className="btn btn-secondary" onClick={saveDraft}>Save Draft</button>
                                <button className="btn btn-primary" onClick={() => alert('This is a demo. Email not sent.')}>Send</button>
                            </div>
                        </div>
                    ) : (
                        <div className="draft-preview-placeholder">
                            Draft will appear here...
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DraftEditor;
