/* ========= GLOBAL STATE ========= */
let selectedRoverId = null;
let pollInterval = null;

/*==========To show Form===========*/
function showForm() {
    const form = document.getElementById("addForm");
    form.style.display = "block";
  }

/* ========= SELECT ROVER ========= */

function selectRover(roverId) {
  selectedRoverId = roverId;
  document.getElementById("selectedRover").innerText = `Rover #${roverId}`;

  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(fetchPosition, 2000);
}

/* ========= SEND COMMAND ========= */
function sendCommand(status) {
  if (!selectedRoverId) {
    alert("Select a rover first");
    return;
  }

  const lat = parseInt(document.getElementById("lat").value);
  const lon = parseInt(document.getElementById("lon").value);

  fetch(`/rover/${selectedRoverId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      lat: lat,
      lon: lon,
      status: status
    })
  })
  .then(res => res.json())
  .then(data => {
    log(`Command sent → ${status}`);
  })
  .catch(err => console.error(err));
}

/* ========= FETCH LIVE POSITION ========= */
function fetchPosition() {
  if (!selectedRoverId) return;

  fetch(`/rover/${selectedRoverId}/position`)
    .then(res => res.json())
    .then(data => {
      document.getElementById("lat").innerText = data.lat;
      document.getElementById("lon").innerText = data.lon;
      document.getElementById("phase").innerText = data.phase;
      document.getElementById("status").innerText = data.status;

      if (data.status === "shift") {
        log("Waiting for master servo operation…");
      }
    })
    .catch(err => console.error(err));
}

/* ========= MASTER RELEASE ========= */
function releaseRover() {
  if (!selectedRoverId) return;

  fetch(`/master/release/${selectedRoverId}`, {
    method: "POST"
  })
  .then(res => res.json())
  .then(data => {
    log("Master released rover");
  })
  .catch(err => console.error(err));
}

/* ========= LOGGING ========= */
function log(message) {
  const logBox = document.getElementById("log");
  const time = new Date().toLocaleTimeString();
  logBox.innerHTML = `[${time}] ${message}<br>` + logBox.innerHTML;
}
