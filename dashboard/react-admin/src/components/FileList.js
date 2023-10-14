import React, { useState } from "react";
import {
  List,
  ListItem,
  ListItemText,
  Button,
  Box,
  useTheme,
  Checkbox,
} from "@mui/material";
// import Check from '@mui/icons-material/Check';
import { tokens } from "./../theme";

const FileList = ({
  files,
  onRemove,
  onPreview,
  onConfirmTrainingFiles,
  confirmedTrainingFiles,
}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const previewTextColor = colors.blueAccent[400];
  const removeTextColor = colors.redAccent[400];
  const confirmedTrainingColor = colors.greenAccent[400];
  const buttonTextcolor = colors.grey[100];

  // State to track selected training files
  const [selectedTrainingFiles, setSelectedTrainingFiles] = useState([]);

  const handleCheckboxChange = (index, isChecked) => {
    if (isChecked) {
      setSelectedTrainingFiles((prev) => [...prev, files[index]]);
    } else {
      setSelectedTrainingFiles((prev) =>
        prev.filter((file) => file !== files[index])
      );
    }
  };

  const confirmTrainingFiles = () => {
    onConfirmTrainingFiles(selectedTrainingFiles);
  };

  return (
    <List>
      {files.map((file, index) => (
        <ListItem key={index} style={{ display: "flex", alignItems: "center" }}>
          <Checkbox
            edge="start"
            checked={selectedTrainingFiles.includes(file)}
            onChange={(e) => handleCheckboxChange(index, e.target.checked)}
            tabIndex={-1}
            disableRipple
            sx={{
              "&.Mui-checked": {
                color: confirmedTrainingColor,
              },
            }}
          />

          <ListItemText
            primary={file.name}
            style={{
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              maxWidth: "250px",
              flex: "1 0 auto",
              fontWeight: confirmedTrainingFiles.includes(file)
                ? "bold"
                : "normal",
              color: confirmedTrainingFiles.includes(file)
                ? confirmedTrainingColor
                : "inherit", // Green if confirmed
            }}
          />
          <Box display="flex" alignItems="center" ml={2} flexShrink={0}>
            <Button
              onClick={() => onPreview(index)}
              style={{ color: previewTextColor, marginRight: "8px" }}
            >
              Preview
            </Button>
            <Button
              onClick={() => onRemove(index)}
              style={{ color: removeTextColor, marginRight: "8px" }}
            >
              Remove
            </Button>
          </Box>
        </ListItem>
      ))}
      {files.length > 0 && (
        <Button
          onClick={confirmTrainingFiles}
          variant="contained"
          style={{
            backgroundColor: colors.primary[400],
            color: buttonTextcolor,
            marginTop: "10px",
          }}
        >
          Confirm Training Files
        </Button>
      )}
    </List>
  );
};

export default FileList;
