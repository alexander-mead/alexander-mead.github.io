// TODO: Read this from a .env file
// const SERVER_URL = "http://127.0.0.1:8000";
const SERVER_URL = "https://worlds-service-1080316704559.europe-west2.run.app";

const ping = () => {
  // Definitions
  const url = SERVER_URL + "/ping";

  // Construct request json
  const params = {
    method: "GET", // Unless this is present it will default to "GET"
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  };

  // Send request
  fetch(url, params)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Ping response:", data);
    })
    .catch((error) => {
      console.log("Error:", error);
    });
};

const image = () => {
  // Definitions
  const url = SERVER_URL + "/worlds";

  // Topography parameters
  const topography = document.getElementById("topography").value;
  const rainfall = document.getElementById("rainfall").value;
  const temperature = document.getElementById("temperature").value;

  // Construct request json
  const params = {
    method: "POST", // Unless this is present it will default to "GET"
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      topography: topography,
      rainfall: rainfall,
      temperature: temperature,
    }),
  };

  // Show spinner and grey overlay
  const spinner = document.getElementById("spinner");
  const overlay = document.getElementById("overlay");
  const button = document.getElementById("clickButton");
  spinner.style.display = "block";
  overlay.style.display = "block";
  button.disabled = true;

  // Send request
  console.log("Request sent");
  console.log("Params: " + JSON.stringify(params));
  fetch(url, params)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then((html) => {
      console.log("Response received");
      // console.log("HTML content:", html); // Log the HTML to verify content
      const iframe = document.getElementById("world");
      if (iframe) {
        iframe.srcdoc = html;
        // Force reflow
        iframe.style.visibility = "hidden";
        void iframe.offsetHeight; // trigger layout
        iframe.style.visibility = "visible";
        console.log("World displayed");
      } else {
        console.error("Element with id 'world' not found");
      }
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
