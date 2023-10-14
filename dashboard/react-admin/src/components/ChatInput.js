import React, { useState } from 'react';
import { useTheme, Button, TextField } from "@mui/material";
import { tokens } from "./../theme";

const ChatInput = ({ onSendMessage, initialPrompt, onInitialPromptResponse }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [message, setMessage] = useState('');
  const buttonTextcolor = colors.grey[100];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      if (initialPrompt) {
        onInitialPromptResponse(message);
      } else {
        onSendMessage(message);
      }
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px' }}>
      <TextField
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message..."
        variant="outlined"
        fullWidth
        style={{ marginRight: '10px' }}
      />
      <Button 
        variant="contained"
        style={{ 
            backgroundColor: colors.primary[400], 
            color: buttonTextcolor
        }}
        type="submit"
      >
        Send
      </Button>
    </form>
  );
};

export default ChatInput;