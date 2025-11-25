import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const Layout = ({ children }) => {
    const location = useLocation();
    const navigate = useNavigate();

    const navItems = [
        { path: '/', label: 'Home', icon: '🏠' },
        { path: '/inbox', label: 'Inbox', icon: '📥' },
        { path: '/drafts', label: 'Drafts', icon: '📝' },
        { path: '/agent', label: 'Email Agent', icon: '🤖' },
        { path: '/brain', label: 'Prompt Brain', icon: '🧠' },
    ];

    return (
        <div className="app-container">
            <div className="navbar">
                <div className="navbar-logo">⚡ Email Agent</div>
                <nav className="nav-links">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                        >
                            {item.label}
                        </Link>
                    ))}
                </nav>
            </div>
            <div className="main-content">
                {location.pathname === '/' ? (
                    <div className="hero-section">
                        <div className="hero-background"></div>
                        <div className="hero-content">
                            <div className="hero-subtitle">Unlock Your Inbox Potential</div>
                            <h1 className="hero-title">Master Your Emails with AI. Automate, Categorize, Respond.</h1>
                            <p className="hero-description">
                                An intelligent, prompt-driven Email Productivity Agent that processes your inbox,
                                automates categorization, extracts action items, drafts replies, and provides chat-based interaction.
                            </p>
                            <div className="hero-buttons">
                                <button className="btn btn-secondary" onClick={() => navigate('/inbox')}>📥 View Inbox</button>
                                <button className="btn btn-primary" onClick={() => navigate('/agent')}>🤖 Chat with Agent</button>
                            </div>
                        </div>
                    </div>
                ) : (
                    children
                )}
            </div>
        </div>
    );
};
export default Layout;
