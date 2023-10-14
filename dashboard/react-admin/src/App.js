import Topbar from "./scenes/global/Topbar";
import { CssBaseline, ThemeProvider } from "@mui/material";
import { ColorModeContext, useMode } from "./theme";
import FileUploadButton from "./components/FileUploadButton";
import React, { useState } from "react";
import FileList from "./components/FileList";
import ChatContainer from "./components/ChatContainer";
import ChatInput from "./components/ChatInput";
import SuggestedFields from "./components/SuggestedFields";
import SelectedFields from "./components/SelectedFields";
import DocumentViewer from "./components/DocumentViewer";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  // DialogContentText,
  DialogActions,
  Button,
} from "@mui/material";
import { tokens } from "./theme";

function App() {
  const [theme, colorMode] = useMode();
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [trainingFiles, setTrainingFiles] = useState([]);
  const [isPreviewOpen, setPreviewOpen] = useState(false);
  const [previewedFileContent, setPreviewedFileContent] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "LLM",
      text: "Please describe your document and its field types.",
    },
  ]);
  const colors = tokens(theme.palette.mode);
  const buttonTextcolor = colors.grey[100];

  // const handleFilesSelected = (files) => {
  //   // Convert the FileList object to an array and add to the uploadedFiles state
  //   setUploadedFiles((prevFiles) => [...prevFiles, ...Array.from(files)]);
  // };
  const handleFilesSelected = async (files) => {
    // Convert the FileList object to an array
    const filesArray = Array.from(files);

    // Update the UI first (optional)
    setUploadedFiles((prevFiles) => [...prevFiles, ...filesArray]);

    // Create a FormData object
    const formData = new FormData();
    filesArray.forEach((file) => {
      formData.append("file", file);
    });

    try {
      // Make a POST request to the Flask API
      const response = await fetch("http://localhost:5000/", {
        // Adjust the URL if your Flask app is hosted elsewhere
        method: "POST",
        body: formData,
      });

      // Check if the request was successful
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      // Process response (if necessary)
      // const data = await response.json();
      // console.log(data); // Log the response for debugging purposes
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  };

  const handleConfirmTrainingFiles = async (selectedFiles) => {
    setTrainingFiles(selectedFiles);

    // // Send the training files to the backend
    // const response = await fetch("/path_to_your_endpoint", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json",
    //   },
    //   body: JSON.stringify({
    //     trainingFiles: selectedFiles,
    //   }),
    // });

    // const data = await response.json();

    // // Check the response from the backend
    // if (data.status === "success") {

    // } else {
    //   // Handle any errors
    //   console.error(data.message);
    // }
  };

  const handleFileRemove = (index) => {
    const fileToRemove = uploadedFiles[index];
    const newFiles = [...uploadedFiles];
    newFiles.splice(index, 1);
    setUploadedFiles(newFiles);

    // Ensure removed file is also removed from training files if it was selected
    setTrainingFiles((prev) => prev.filter((file) => file !== fileToRemove));
  };

  const handleFilePreview = (index) => {
    // This is just a placeholder. In a real scenario, you'd read the file contents.
    const fileContent = "Contents of the file " + uploadedFiles[index].name;
    setPreviewedFileContent(fileContent);
    setPreviewOpen(true);
  };

  const [initialPrompt, setInitialPrompt] = useState(true); // Assuming you want the initial prompt to show up immediately.

  const handleInitialPromptResponse = async (message) => {
    // Add user's response to the chat
    setMessages([...messages, { sender: "user", text: message }]);

    // Send the user's input to the backend
    try {
      const response = await fetch(
        "http://localhost:5000/initiate_conversation",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_input: message,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();

      // Update the chat with the LLM's response
      setMessages((prev) => [
        ...prev,
        { sender: "LLM", text: data.naturalResponse },
      ]);

      // Update the suggested fields (if any)
      if (data.fields && data.fields.length) {
        setSuggestedFields(
          data.fields.map((field) => ({ id: field, name: field }))
        );
      }

      // Update the selected fields (if any)
      if (data.confirmed_fields && data.confirmed_fields.length) {
        setSelectedFields((prev) => [
          ...prev,
          ...data.confirmed_fields.map((field) => ({ id: field, name: field })),
        ]);
      }
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
      // Handle the error. Maybe update the chat with an error message or show an alert.
    }

    // Set initialPrompt to false since we've handled the initial response
    setInitialPrompt(false);
  };

  // const handleSendMessage = (text) => {
  //   // Add user's message to the chat
  //   setMessages([...messages, { sender: "user", text }]);

  //   // call backend API to get the LLM's response
  //   // For demonstration purposes, dummy response
  //   setTimeout(() => {
  //     setMessages([
  //       ...messages,
  //       { sender: "user", text },
  //       { sender: "LLM", text: "This is LLM's response" },
  //     ]);
  //   }, 1000);
  // };
  const handleSendMessage = async (text) => {
    // Add user's message to the chat
    setMessages([...messages, { sender: "user", text }]);

    try {
      const response = await fetch(
        "http://localhost:5000/handle_user_message",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_input: text,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();

      // Update the chat with the LLM's response
      setMessages((prev) => [
        ...prev,
        { sender: "LLM", text: data.naturalResponse },
      ]);

      // Update the suggested fields based on the response
      if (data.suggested_fields && data.suggested_fields.length) {
        setSuggestedFields(
          data.suggested_fields.map((field) => ({ id: field, name: field }))
        );
      }

      // If the response contains any confirmed or rejected fields, update them accordingly
      if (data.confirmed_fields && data.confirmed_fields.length) {
        setSelectedFields((prev) => [
          ...prev,
          ...data.confirmed_fields.map((field) => ({ id: field, name: field })),
        ]);
      }
      if (data.rejected_fields && data.rejected_fields.length) {
        setRejectedFields((prev) => [
          ...prev,
          ...data.rejected_fields.map((field) => ({ id: field, name: field })),
        ]);
      }
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
      // Handle the error, for instance, by showing an error message to the user
    }
  };

  const [suggestedFields, setSuggestedFields] = useState([]); // Fetch these from your API
  // const [suggestedFields, setSuggestedFields] = useState([
  //   { id: "a", name: "Field A" },
  //   { id: "b", name: "Field B" },
  //   { id: "c", name: "Field C" },
  // ]);
  const [selectedFields, setSelectedFields] = useState([]);
  const [rejectedFields, setRejectedFields] = useState([]);

  // const onFieldAction = (itemId, action) => {
  //   const targetField = suggestedFields.find((field) => field.id === itemId);
  //   if (targetField) {
  //     setSuggestedFields((prev) => prev.filter((field) => field.id !== itemId));
  //     if (action === "select") {
  //       setSelectedFields((prev) => [...prev, targetField]);
  //     } else if (action === "reject") {
  //       setRejectedFields((prev) => [...prev, targetField]);
  //     }
  //   }
  // };
  const onFieldAction = async (itemId, action) => {
    const targetField = suggestedFields.find((field) => field.id === itemId);
    if (targetField) {
      let newSelectedFields = [...selectedFields];
      let newRejectedFields = [...rejectedFields];
      let newSuggestedFields = suggestedFields.filter(
        (field) => field.id !== itemId
      );

      if (action === "select") {
        newSelectedFields.push(targetField);
      } else if (action === "reject") {
        newRejectedFields.push(targetField);
      }

      // Prepare the payload with the new state
      const payload = {
        confirmed_fields: newSelectedFields.map((f) => f.name),
        rejected_fields: newRejectedFields.map((f) => f.name),
        suggested_fields: newSuggestedFields.map((f) => f.name),
      };

      const response = await fetch("http://localhost:5000/modify_fields", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      // console.log("Before sending:", payload);
      const data = await response.json();
      // console.log("Response from server:", data);

      // Update front-end arrays based on the response from the back-end
      setSuggestedFields(
        data.suggested_fields.map((field) => ({ id: field, name: field }))
      );
      setSelectedFields(
        data.confirmed_fields.map((field) => ({ id: field, name: field }))
      );
      setRejectedFields(
        data.rejected_fields.map((field) => ({ id: field, name: field }))
      );
    }
  };

  const handleFieldUnselect = (fieldId) => {
    let unselectedItem = selectedFields.find((field) => field.id === fieldId);
    if (unselectedItem) {
      setSelectedFields((prev) => prev.filter((field) => field.id !== fieldId));
    } else {
      unselectedItem = rejectedFields.find((field) => field.id === fieldId);
      if (unselectedItem) {
        setRejectedFields((prev) =>
          prev.filter((field) => field.id !== fieldId)
        );
      }
    }
    if (unselectedItem) {
      setSuggestedFields((prev) => [...prev, unselectedItem]);
    }
  };

  const handleGenerateMapping = async (documentName) => {
    try {
      const response = await fetch(
        "http://localhost:5000/complete_doc_fields",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            document_name: documentName,
            finalized_fields: selectedFields,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      // const data = await response.json();
      // Handle the received data, e.g., display the mapping to the user or allow them to download it
      // You can use data.fields_mapping, data.document_name, and data.document_content as needed
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  };

  const handleBulkProcess = async (documentName) => {
    try {
      const response = await fetch("http://localhost:5000/bulk_process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_name: documentName,
          finalized_fields: selectedFields,
        }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      // const data = await response.json();
      // Handle the received data, e.g., display the mapping to the user or allow them to download it
      // You can use data.fields_mapping, data.document_name, and data.document_content as needed
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  };

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <div className="app">
          <main className="content">
            <Topbar />
            <div className="centeredContainer">
              <FileUploadButton onFilesSelected={handleFilesSelected} />
              <FileList
                files={uploadedFiles}
                confirmedTrainingFiles={trainingFiles} // Pass this prop to FileList
                onRemove={handleFileRemove}
                onPreview={handleFilePreview}
                onConfirmTrainingFiles={handleConfirmTrainingFiles}
              />
            </div>

            {/* Training Document Viewer */}
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                padding: "20px 0",
              }}
            >
              <div
                style={{
                  width: "60%",
                  padding: "0 20px",
                }}
              >
                {trainingFiles.length > 0 && (
                  <DocumentViewer trainingFile={trainingFiles[0]} />
                )}
              </div>
            </div>

            {/* Chat UI */}
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                padding: "20px 0",
              }}
            >
              <div
                style={{
                  width: "60%",
                  padding: "0 20px",
                }}
              >
                {trainingFiles.length > 0 && (
                  <div>
                    <ChatContainer messages={messages} />
                    <ChatInput
                      onSendMessage={handleSendMessage}
                      initialPrompt={initialPrompt}
                      onInitialPromptResponse={handleInitialPromptResponse}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Fields UI */}
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                padding: "20px",
              }}
            >
              <div
                style={{
                  flex: 1,
                  padding: "0 20px",
                  border: "1px solid #ccc",
                  marginRight: "20px",
                }}
              >
                <h3>Suggested Fields</h3>
                <SuggestedFields
                  items={suggestedFields}
                  onFieldAction={onFieldAction}
                />
              </div>
              <div
                style={{
                  flex: 1,
                  padding: "0 20px",
                  border: "1px solid #ccc",
                  marginRight: "20px",
                }}
              >
                <h3>Selected Fields</h3>
                <SelectedFields
                  items={selectedFields}
                  onUnselect={handleFieldUnselect}
                />
              </div>
              <div
                style={{ flex: 1, padding: "0 20px", border: "1px solid #ccc" }}
              >
                <h3>Rejected Fields</h3>
                <SelectedFields
                  items={rejectedFields}
                  onUnselect={handleFieldUnselect}
                />
              </div>
            </div>

            {/* Generate Mapping */}
            {/* <button
              onClick={() => handleGenerateMapping(trainingFiles[0].name)}
            >
              Test File Mapping
            </button> */}

            <Button
              variant="contained"
              style={{
                backgroundColor: colors.blueAccent[700],
                color: buttonTextcolor,
              }}
              onClick={() => handleGenerateMapping(trainingFiles[0].name)}
              sx={{ mt: 2, mb: 2 }}
            >
              Test File Mapping
            </Button>

            {/* Generate Bulk Process*/}
            {/* <button onClick={() => handleBulkProcess(trainingFiles[0].name)}>
              Generate All File Mappings
            </button> */}
            <Button
              variant="contained"
              style={{
                backgroundColor: colors.greenAccent[700],
                color: buttonTextcolor,
              }}
              onClick={() => handleBulkProcess(trainingFiles[0].name)}
              sx={{ mt: 2, mb: 2 }}
            >
              Generate All File Mappings
            </Button>
          </main>

          <Dialog
            open={isPreviewOpen}
            onClose={() => setPreviewOpen(false)}
            aria-labelledby="file-preview-title"
            fullWidth
            maxWidth="md"
          >
            <DialogTitle id="file-preview-title">File Preview</DialogTitle>
            <DialogContent>
              <pre>{previewedFileContent}</pre>
            </DialogContent>
            <DialogActions>
              <Button
                onClick={() => setPreviewOpen(false)}
                style={{ color: buttonTextcolor }}
              >
                Close
              </Button>
            </DialogActions>
          </Dialog>
        </div>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export default App;
