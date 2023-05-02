const baseURL = "http://127.0.0.1:3000";
// const baseURL = "https://birlzhi2xg.execute-api.eu-west-2.amazonaws.com/Prod";

const image = () => {
  // Definitions
  const url = baseURL + "/nbody";

  // Get from html
  const Omega_m = document.getElementById("Omega_m").value;
  const Omega_b = document.getElementById("Omega_b").value;
  const H_0 = document.getElementById("H_0").value;
  const sigma_8 = document.getElementById("sigma_8").value;
  const n_s = document.getElementById("n_s").value;

  // Calculate
  // const zoom = 2 ** document.getElementById("zoom").value;
  // const transform = 1 / (1 + Math.log(depth / 64) / Math.log(2));

  // Constants
  const kmin = 1e-3;
  const kmax = 1e1;
  const nk = 100;
  const z = 0;
  const npix = 512;
  const Lbox = 512;

  // Construct json
  const params = {
    method: "POST", // Unless this is present it will default to "GET"
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      kmin: kmin,
      kmax: kmax,
      nk: nk,
      z: z,
      npix: npix,
      Lbox: Lbox,
      Omega_m: Omega_m,
      Omega_b: Omega_b,
      H_0: H_0,
      sigma_8: sigma_8,
      n_s: n_s,
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
