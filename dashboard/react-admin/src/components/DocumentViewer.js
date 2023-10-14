import React, { useState, useEffect } from "react";

const DocumentViewer = ({ trainingFile }) => {
  console.log("Training File:", trainingFile);

  const [documentContent, setDocumentContent] = useState("");

  useEffect(() => {
    const fetchDocumentContent = async () => {
      try {
        const response = await fetch("http://localhost:5000/select_file", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            selected_file: trainingFile.name,
          }),
        });
        const data = await response.json();
        console.log("Document data:", data);

        if (data.status === "success") {
          setDocumentContent(data.document_content);
        } else {
          console.error(data.message);
        }
      } catch (error) {
        console.error("Error fetching document content:", error);
      }
    };

    if (trainingFile) {
      fetchDocumentContent();
    }
  }, [trainingFile]);

  return (
    <div className="document-viewer">
      <pre>{documentContent}</pre>
    </div>
  );
};

export default DocumentViewer;
