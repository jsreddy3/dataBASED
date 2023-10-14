import React, { useState } from 'react';
import {useTheme, Button, Box } from "@mui/material";
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { tokens } from "./../theme";

const FileUploadButton = ({ onFilesSelected }) => {
    const [uploaded, setUploaded] = useState(false);
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const fileInputRef = React.createRef();
    const buttonTextcolor = colors.grey[100];

    const handleButtonClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = (event) => {
        const files = event.target.files;
        if (files.length > 0 && onFilesSelected) {
            onFilesSelected(files);
            setUploaded(true);  // Indicate that files have been uploaded
        }
    };

    return (
        <Box display="flex" flexDirection="column" alignItems="center">
            <input 
                type="file" 
                style={{ display: 'none' }} 
                multiple 
                ref={fileInputRef}
                onChange={handleFileChange} 
            />
            <Button 
                variant="contained" 
                style={{ 
                    backgroundColor: colors.primary[400], 
                    color: buttonTextcolor
                }}
                onClick={handleButtonClick}
                sx={{ mt: 2, mb: 2 }}
            >
                Upload Files
            </Button>
            {uploaded && <CheckCircleIcon color="success" />}  {/* Display the checkmark if uploaded */}
        </Box>
    );
};

export default FileUploadButton;