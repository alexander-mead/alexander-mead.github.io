// TODO: Read this from a .env file
// const SERVER_URL = "http://127.0.0.1:3000"; // local
const SERVER_URL =
  "https://wfa3ikw7ra.execute-api.eu-west-2.amazonaws.com/Prod"; // Personal cloud
const API_KEY = "tb7mB97zld20ehqsWK9tM7gRpJG27RpF4hfZQ8pj";

const image = () => {
  // Definitions
  const url = SERVER_URL + "/nbody";

  // Cosmological parameters
  const Omega_m = document.getElementById("Omega_m").value;
  const Omega_b = document.getElementById("Omega_b").value;
  const H_0 = document.getElementById("H_0").value;
  const A_s = 2e-9;
  const n_s = document.getElementById("n_s").value;
  const w_0 = document.getElementById("w_0").value;
  const w_a = 0.0;
  const m_nu = 0.0;

  // Color scheme
  const color = document.getElementById("color").value;

  // Seed
  let seed = document.getElementById("seed").value;
  if (seed === "random") {
    seed = null;
  }

  // Constants
  const npix = 1000.0;
  const Lbox = 500.0;
  const Tbox = 1.0;

  // Construct json
  const params = {
    method: "POST", // Unless this is present it will default to "GET"
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": API_KEY,
      Accept: "application/json",
    },
    body: JSON.stringify({
      color: color,
      npix: npix,
      Lbox: Lbox,
      Tbox: Tbox,
      Omega_m: Omega_m,
      Omega_b: Omega_b,
      H_0: H_0,
      A_s: A_s,
      n_s: n_s,
      w_0: w_0,
      w_a: w_a,
      m_nu: m_nu,
      seed: seed,
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
  console.log("Params: " + JSON.stringify(params));
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
