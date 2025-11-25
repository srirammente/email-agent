import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Inbox from './components/Inbox';
import AgentChat from './components/AgentChat';
import PromptBrain from './components/PromptBrain';
import EmailDetail from './components/EmailDetail';
import DraftList from './components/DraftList';
import DraftLoader from './components/DraftLoader';
import './App.css';

function App() {
  const [selectedEmail, setSelectedEmail] = useState(null);

  return (
    <Layout selectedEmail={selectedEmail}>
      <Routes>
        <Route path="/" element={null} />
        <Route path="/inbox" element={<Inbox setSelectedEmail={setSelectedEmail} />} />
        <Route path="/inbox/:emailId" element={<EmailDetail />} />
        <Route path="/drafts" element={<DraftList onSelectDraft={(d) => window.location.href = `/drafts/${d.id}`} />} />
        <Route path="/drafts/:draftId" element={<DraftLoader />} />
        <Route path="/agent" element={<AgentChat emailId={selectedEmail ? selectedEmail.id : null} />} />
        <Route path="/brain" element={<PromptBrain />} />
      </Routes >
    </Layout >
  );
}

export default App;
