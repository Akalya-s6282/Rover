/* ========= GLOBAL STATE ========= */
let selectedRoverId = null;
let pollInterval = null;

/*==========To show Form===========*/
function showForm() {
    const form = document.getElementById("addForm");
    form.style.display = "block";
  }

function show_latitudegpio() {
  const gpioSection = document.getElementById("gpioSection");
  gpioSection.style.display = "block";
  }

// Build GPIO input rows based on entered total latitudes (client-side)
function buildGpioInputs() {
  const totalInput = document.querySelector('input[name="total_latitudes"]');
  const total = parseInt(totalInput.value);
  if (!total || total <= 0) {
    alert('Enter a positive number for total latitudes');
    return;
  }

  const container = document.getElementById('gpioInputsContainer');
  container.innerHTML = '';

  for (let i = 1; i <= total; i++) {
    const row = document.createElement('div');
    row.className = 'gpio-row';

    const label = document.createElement('label');
    label.innerText = `Latitude ${i}:`;

    const hiddenIndex = document.createElement('input');
    hiddenIndex.type = 'hidden';
    hiddenIndex.name = 'latitude_index';
    hiddenIndex.value = i;

    const gpioInput = document.createElement('input');
    gpioInput.type = 'number';
    gpioInput.name = 'gpio_pin';
    gpioInput.placeholder = 'GPIO pin number';
    gpioInput.required = true;

    row.appendChild(label);
    row.appendChild(hiddenIndex);
    row.appendChild(gpioInput);

    container.appendChild(row);
  }

  // show section and set hidden total value
  document.getElementById('gpioSection').style.display = 'block';
  document.getElementById('totalLatHidden').value = total;
  const notice = document.getElementById('gpioSavedNotice');
  notice.style.display = 'block';
}

// Attach handler to the Show button after DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('showGpioBtn');
  if (btn) btn.addEventListener('click', buildGpioInputs);
});

// /* ========= SELECT ROVER ========= */

// function selectRover(roverId) {
//   selectedRoverId = roverId;
//   document.getElementById("selectedRover").innerText = `Rover #${roverId}`;

//   if (pollInterval) clearInterval(pollInterval);
//   pollInterval = setInterval(fetchPosition, 2000);
// }

// /* ========= SEND COMMAND ========= */
// function sendCommand(status) {
//   if (!selectedRoverId) {
//     alert("Select a rover first");
//     return;
//   }

//   const lat = parseInt(document.getElementById("lat").value);
//   const lon = parseInt(document.getElementById("lon").value);

//   fetch(`/rover/${selectedRoverId}`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({
//       lat: lat,
//       lon: lon,
//       status: status
//     })
//   })
//   .then(res => res.json())
//   .then(data => {
//     log(`Command sent → ${status}`);
//   })
//   .catch(err => console.error(err));
// }

// /* ========= FETCH LIVE POSITION ========= */
// function fetchPosition() {
//   if (!selectedRoverId) return;

//   fetch(`/rover/${selectedRoverId}/position`)
//     .then(res => res.json())
//     .then(data => {
//       document.getElementById("lat").innerText = data.lat;
//       document.getElementById("lon").innerText = data.lon;
//       document.getElementById("phase").innerText = data.phase;
//       document.getElementById("status").innerText = data.status;

//       if (data.status === "shift") {
//         log("Waiting for master servo operation…");
//       }
//     })
//     .catch(err => console.error(err));
// }

// /* ========= MASTER RELEASE ========= */
// function releaseRover() {
//   if (!selectedRoverId) return;

//   fetch(`/master/release/${selectedRoverId}`, {
//     method: "POST"
//   })
//   .then(res => res.json())
//   .then(data => {
//     log("Master released rover");
//   })
//   .catch(err => console.error(err));
// }

// /* ========= LOGGING ========= */
// function log(message) {
//   const logBox = document.getElementById("log");
//   const time = new Date().toLocaleTimeString();
//   logBox.innerHTML = `[${time}] ${message}<br>` + logBox.innerHTML;
// }
// // 