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

function adjustTextareaHeight(textarea) {
  textarea.style.height = 'auto';  // Reset height
  textarea.style.height = (textarea.scrollHeight) + 'px';  // Set to content height
}

function displaySelectedFileContent(content) {
  let displayArea = document.getElementById("fileContentDisplay");
  if (displayArea) {
      displayArea.value = content;
      adjustTextareaHeight(displayArea);
  }
}

function displayFields(fields, descriptions) {
  const suggestedBox = document.getElementById("suggestedFieldsBox");

  // Clear any existing items in the suggestedBox
  suggestedBox.innerHTML = '';

  fields.forEach((field, index) => {
      let listItem = document.createElement("li");

      // Create a text node for the field name and a button for selecting
      let fieldText = document.createTextNode(field + " - " + descriptions[index] + " ");
      let selectButton = document.createElement("button");

      // Configure the select button
      selectButton.textContent = "Select";
      selectButton.onclick = function() {
          moveFieldToSelected(field);
          listItem.remove();  // Remove the field from the suggested box
      };

      // Append the text node and button to the list item, then the list item to the suggestedBox
      listItem.appendChild(fieldText);
      listItem.appendChild(selectButton);
      suggestedBox.appendChild(listItem);
  });
}


// Process user's message
function processUserMessage(message) {
  // Send the user's message to the Flask backend
  fetch('/process_message', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({message: message})
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
      }
      return response.json();
  })
  .then(data => {
      const functionCall = data.function_call;  // Adjusted to match the Python code
      if(functionCall && functionCall.name === 'identify_fields') {
          // Assuming args contains fields, descriptions, and naturalResponse properties
          const {fields, descriptions, naturalResponse} = functionCall.arguments;

          // Display the suggested fields with their descriptions
          displayFields(fields, descriptions);

          // Display the natural language response in the chat box
          addMessageToChat("Bot", naturalResponse.trim());
      } else {
          console.error("Unexpected response format:", data);
      }
  })
  .catch(error => {
      console.error('There has been a problem with your fetch operation:', error);
  });
}

function moveFieldToSelected(field) {
  const selectedBox = document.getElementById("selectedFieldsBox");
  let listItem = document.createElement("li");
  
  let fieldText = document.createTextNode(field);  // Create a text node for the field name
  listItem.appendChild(fieldText);  // Append the text node to the list item
  
  let deselectButton = document.createElement("button");  // Create a deselect button
  deselectButton.textContent = "Deselect";
  deselectButton.onclick = function() {
      moveFieldToSuggested(field);
      listItem.remove();
  };
  listItem.appendChild(deselectButton);  // Append the deselect button to the list item
  
  selectedBox.appendChild(listItem);  // Add to the 'Selected Fields' box
}

function moveFieldToSuggested(field) {
  const suggestedBox = document.getElementById("suggestedFieldsBox");
  let listItem = document.createElement("li");
  
  let fieldText = document.createTextNode(field);  // Create a text node for the field name
  listItem.appendChild(fieldText);  // Append the text node to the list item
  
  let selectButton = document.createElement("button");  // Create a select button
  selectButton.textContent = "Select";
  selectButton.onclick = function() {
      moveFieldToSelected(field);
      listItem.remove();
  };
  listItem.appendChild(selectButton);  // Append the select button to the list item
  
  suggestedBox.appendChild(listItem);  // Add to the 'Suggested Fields' box
}

// Start the chat
initChat();