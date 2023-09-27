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
  });
}

// Fetch and display files once the page is loaded
window.onload = fetchAndDisplayFiles;
