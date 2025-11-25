import React, { useState, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import ReactMarkdown from 'react-markdown';

const AgentChat = ({ emailId }) => {
    const [messages, setMessages] = useState([
        { role: 'agent', content: 'Hello! I\'m your Email Agent. I can help you:\n\n• Summarize emails\n• Find action items\n• Answer questions about your inbox\n• Draft replies\n\nWhat would you like to know?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

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

    return (
        <div className="card chat-container">
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
