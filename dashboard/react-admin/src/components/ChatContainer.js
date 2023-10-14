// ChatContainer.js
import React from 'react';

const ChatContainer = ({ messages }) => {
  return (
    <div style={{ maxHeight: '400px', overflowY: 'scroll', border: '1px solid gray', padding: '10px' }}>
      {messages.map((message, index) => (
        <div key={index} style={{ marginBottom: '10px' }}>
          {message.sender === 'user' ? (
            <div style={{ textAlign: 'right' }}>
              {message.text}
            </div>
          ) : (
            <div style={{ textAlign: 'left' }}>
              {message.text}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ChatContainer;