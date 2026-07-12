import { useState } from 'react';
import ChatMessage from '../components/ChatMessage.jsx';
import ChatInput from '../components/ChatInput.jsx';
import { sendChat } from '../services/api.js';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(null);

  async function handleSend(text) {
    const userMsg = { role: 'user', content: text };
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((prev) => [...prev, userMsg]);
    setPending(true);
    setError(null);
    try {
      const reply = await sendChat(text, history);
      setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="chat-page">
      <header className="chat-header">
        <h1>AI DevOps Copilot</h1>
      </header>
      <main className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            Ask about runbooks, deployments, or incidents.
          </div>
        )}
        {messages.map((m, i) => (
          <ChatMessage key={i} role={m.role} content={m.content} />
        ))}
        {pending && <ChatMessage role="assistant" content="…" />}
        {error && <div className="chat-error">{error}</div>}
      </main>
      <ChatInput onSend={handleSend} disabled={pending} />
    </div>
  );
}
