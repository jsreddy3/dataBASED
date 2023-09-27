// Function to fetch uploaded files and display them
function fetchAndDisplayFiles() {
  fetch('/get_files')
      .then(response => response.json())
      .then(data => {
          let files = data.files;
          let fileList = document.getElementById("uploadedFiles");

          // Clear current list
          fileList.innerHTML = '';

          files.forEach(file => {
              let listItem = document.createElement("li");
              let checkbox = document.createElement("input");
              checkbox.type = "checkbox";
              checkbox.value = file;
              listItem.appendChild(checkbox);
              listItem.appendChild(document.createTextNode(file));
              fileList.appendChild(listItem);
          });
      });
}


// Function to submit selected files
function submitSelectedFiles() {
  let checkboxes = document.querySelectorAll("#uploadedFiles input[type='checkbox']");
  let selectedFiles = [];

  checkboxes.forEach(checkbox => {
      if (checkbox.checked) {
          selectedFiles.push(checkbox.value);
      }
  });

  fetch('/select_files', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({selected_files: selectedFiles})
  })
  .then(response => response.json())
  .then(data => {
      // Handle response; for now, we just alert the user
      alert("Files selected successfully!");
      displaySelectedFileContent(data.first_file_content);
  });
}

function displaySelectedFileContent(content) {
  // Assuming you have a <div> or <textarea> with id "fileContentDisplay" for displaying the file content
  let displayArea = document.getElementById("fileContentDisplay");
  if (displayArea) {
      displayArea.value = content; // If it's a textarea
      // OR 
      // displayArea.innerText = content; // If it's a div or other text container
  }
}

// Fetch and display files once the page is loaded
window.onload = fetchAndDisplayFiles;

// ... existing content ...

// Initialize chat by asking the first question
function initChat() {
  addMessageToChat("Bot", "What type of documents are you uploading?");
}

// Send a message to the chat box
function addMessageToChat(sender, message) {
  const chatBox = document.getElementById("chatBox");
  const msgElem = document.createElement("div");
  msgElem.className = sender;
  msgElem.textContent = message;
  chatBox.appendChild(msgElem);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// User sends a message
function sendMessage() {
  const inputElem = document.getElementById("userInput");
  const userMessage = inputElem.value;

  if (userMessage.trim() === '') return;

  addMessageToChat("User", userMessage);
  inputElem.value = "";

  // Process the message
  processUserMessage(userMessage);
}

// Process user's message
function processUserMessage(message) {
  // Here, you can interact with GPT API and take actions based on message content.
  // For now, as a placeholder, we will simulate a GPT response.
  setTimeout(() => {
      addMessageToChat("Bot", "Thanks for sharing! Based on your input, I'd recommend these fields: ...");
  }, 1000);
}

// Start the chat
initChat();