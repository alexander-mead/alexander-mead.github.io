// const baseURL = "http://127.0.0.1:3000";
const baseURL = "https://3ptm05v8lb.execute-api.eu-west-1.amazonaws.com/Prod";

const image = () => {
  // Definitions
  const url = baseURL + "/mandelbrot";

  // Get from html
  const real = document.getElementById("real").value;
  const imag = document.getElementById("imag").value;
  const zoom = document.getElementById("zoom").value;
  const depth = document.getElementById("depth").value;
  const color = document.getElementById("color").value;
  const width = 750;
  const height = 750;
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
    }),
  };

  // Fetch
  console.log("Request sent");
  fetch(url, params)
    .then((response) => response.json()) // TODO: Not blob; maybe use response.blob()?
    .then((blob) => {
      console.log("Response blob received");
      console.log("Blob: " + blob);
      //console.log(blob);
      //const objectURL = blob.data;
      const data = blob.data;
      const image = "data:image/png;base64," + data;
      //console.log("Image: "+image);
      document.getElementById("image").src = image; // To set image within html
      console.log("Image displayed");
    })
    // TODO: Disable button to prevent multiple requests
    //.then(document.getElementById("buttonId").disabled = true)
    .catch((error) => {
      console.log("Error:", error);
      console.log("Failed to sample image");
    });
};
