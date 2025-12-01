import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import ReactMarkdown from 'react-markdown';

const AgentChat = ({ emailId: propEmailId }) => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    // Prioritize URL parameter over prop
    const emailId = searchParams.get('emailId') || propEmailId;

    const [messages, setMessages] = useState([
        { role: 'agent', content: 'Hello! I\'m your Email Agent. I can help you:\n\n• Summarize emails\n• Find action items\n• Answer questions about your inbox\n• Draft replies\n\nWhat would you like to know?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showDraftConfirmation, setShowDraftConfirmation] = useState(false);
    const [pendingDraftInstructions, setPendingDraftInstructions] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        // Check for draft intent
        const draftKeywords = ['draft', 'reply', 'write a response', 'compose', 'send a reply', 'write back'];
        const hasDraftIntent = draftKeywords.some(keyword =>
            input.toLowerCase().includes(keyword)
        );

        // If draft intent detected and we have an email context, show confirmation
        if (hasDraftIntent && emailId) {
            setPendingDraftInstructions(input);
            setShowDraftConfirmation(true);
            return; // Don't send the message yet
        }

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE_URL}/agent/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: userMsg.content,
                    email_id: emailId,
                    history: messages
                })
            });
            const data = await res.json();
            setMessages(prev => [...prev, { role: 'agent', content: data.response }]);
        } catch (e) {
            setMessages(prev => [...prev, { role: 'agent', content: '❌ Sorry, I encountered an error. Please try again.' }]);
        }
        setLoading(false);
    };

    const handleDraftConfirm = async () => {
        setShowDraftConfirmation(false);
        const userMsg = { role: 'user', content: pendingDraftInstructions };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            // Generate draft
            const res = await fetch(`${API_BASE_URL}/drafts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_id: emailId,
                    instructions: pendingDraftInstructions
                })
            });
            const draft = await res.json();

            // Show success message
            setMessages(prev => [...prev, {
                role: 'agent',
                content: '✅ Draft generated successfully! Redirecting you to the draft editor...'
            }]);

            // Redirect to draft editor after a short delay
            setTimeout(() => {
                navigate(`/drafts/${draft.id}`);
            }, 1500);
        } catch (e) {
            setMessages(prev => [...prev, {
                role: 'agent',
                content: '❌ Sorry, I encountered an error generating the draft. Please try again.'
            }]);
        }
        setLoading(false);
        setPendingDraftInstructions('');
    };

    const handleDraftCancel = () => {
        setShowDraftConfirmation(false);
        setPendingDraftInstructions('');
        // Continue with normal chat
        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
    };

    return (
        <div className="card chat-container">
            {/* Draft Confirmation Modal */}
            {showDraftConfirmation && (
                <div className="modal-overlay" onClick={() => setShowDraftConfirmation(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>📝 Draft Reply</h3>
                        <p>Would you like me to generate a draft reply for this email?</p>
                        <div className="modal-actions">
                            <button className="btn btn-secondary" onClick={handleDraftCancel}>
                                No, continue chat
                            </button>
                            <button className="btn btn-primary" onClick={handleDraftConfirm}>
                                Yes, create draft
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="card-header chat-header">
                <div className="chat-header-content">
                    <div className="chat-avatar-header">🤖</div>
                    <div>
                        <h2 className="card-title">Email Agent</h2>
                        <p className="chat-status">Online • Ready to help</p>
                    </div>
                </div>
            </div>

            <div className="chat-messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`chat-message-wrapper ${msg.role}`}>
                        <div className="chat-avatar">
                            {msg.role === 'agent' ? '🤖' : '👤'}
                        </div>
                        <div className={`chat-bubble ${msg.role}`}>
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="chat-message-wrapper agent">
                        <div className="chat-avatar">🤖</div>
                        <div className="chat-bubble agent typing">
                            <span className="typing-dot"></span>
                            <span className="typing-dot"></span>
                            <span className="typing-dot"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-container">
                <input
                    type="text"
                    className="chat-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask me anything about your emails..."
                />
                <button
                    className="chat-send-btn"
                    onClick={sendMessage}
                    disabled={loading || !input.trim()}
                >
                    {loading ? '⏳' : '📤'}
                </button>
            </div>
        </div>
    );
};

export default AgentChat;
