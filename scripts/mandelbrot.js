// TODO: Read this from a .env file
// const baseURL = "http://127.0.0.1:3000"; // local
// const baseURL = "https://qte7wuo072.execute-api.eu-west-2.amazonaws.com/Prod"; // digiLab cloud
const baseURL = "https://x7or5gwlkk.execute-api.eu-west-2.amazonaws.com/Prod"; // Personal cloud

const image = () => {
  // Definitions
  const url = baseURL + "/mandelbrot";

  // Get from html
  const real = document.getElementById("real").value;
  const imag = document.getElementById("imag").value;
  const depth = document.getElementById("depth").value;
  const color = document.getElementById("color").value;

  // Calculate
  const zoom = 2 ** document.getElementById("zoom").value;
  const transform = 1 / (1 + Math.log(depth / 64) / Math.log(2));

  // Constants
  const width = 1000;
  const height = 1000;
  const sigma = 0.5;

  // Construct json
  const params = {
    method: "POST", // Unless this is present it will default to "GET"
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      real: real,
      imag: imag,
      zoom: zoom,
      depth: depth,
      color: color,
      width: width,
      height: height,
      sigma: sigma,
      transform: transform,
    }),
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
  fetch(url, params)
    .then((response) => response.json()) // TODO: Not blob; maybe use response.blob()?
    .then((blob) => {
      console.log("Response blob received");
      console.log("Blob: " + blob);
      const data = blob.data;
      const image = "data:image/png;base64," + data;
      document.getElementById("image").src = image; // To set image within html
      console.log("Image displayed");
      spinner.style.display = "none";
      overlay.style.display = "none";
      button.disabled = false;
    })
    .catch((error) => {
      console.log("Error:", error);
      console.log("Failed to sample image");
      spinner.style.display = "none";
      overlay.style.display = "none";
      button.disabled = false;
    });
};
