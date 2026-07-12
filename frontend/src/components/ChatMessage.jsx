export default function ChatMessage({ role, content }) {
  return (
    <div className={`chat-message chat-message-${role}`}>
      <div className="chat-message-role">{role}</div>
      <div className="chat-message-content">{content}</div>
    </div>
  );
}
