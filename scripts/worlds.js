// TODO: Read this from a .env file
const SERVER_URL = "http://127.0.0.1:8000"; // local

const image = () => {
  // Definitions
  const url = SERVER_URL + "/worlds";

  // Construct json
  const params = {
    method: "POST", // Unless this is present it will default to "GET"
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  };

  // Show spinner and grey overlay
  const spinner = document.getElementById("spinner");
  const overlay = document.getElementById("overlay");
  const button = document.getElementById("clickButton");
  spinner.style.display = "block";
  overlay.style.display = "block";
  button.disabled = true;

  // Fetch
  console.log("Request sent");
  console.log("Params: " + JSON.stringify(params));
  fetch(url, params)
    .then((response) => response.json())
    .then((blob) => {
      console.log("Response received");
      const html = blob.html;
      document.getElementById("world").src = html; // To set image within html
      console.log("World displayed");
      spinner.style.display = "none";
      overlay.style.display = "none";
      button.disabled = false;
    })
    .catch((error) => {
      console.log("Error:", error);
      console.log("Failed to display world");
      spinner.style.display = "none";
      overlay.style.display = "none";
      button.disabled = false;
    });
};
