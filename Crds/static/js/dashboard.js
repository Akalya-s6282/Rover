/* ========= GLOBAL STATE ========= */
let selectedRoverId = null;
let pollInterval = null;

/*========== Toggle Form Modal ===========*/
function toggleForm() {
    const modal = document.getElementById("formModal");
    modal.classList.toggle("show");
}

document.querySelectorAll('.rover-block').forEach(block => {
  block.addEventListener('click', e => {
    if (!e.target.closest('form')) {
      window.location.href = block.dataset.url;
    }
  });
});

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById("formModal");
    if (event.target === modal) {
        modal.classList.remove("show");
    }
});

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
    label.innerText = `Aile ${i}:`;

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

function getStatusDotClass(statusValue) {
  const s = String(statusValue || '').toLowerCase();
  if (s.includes('busy') || s.includes('transit') || s === 'delivering' || s === 'in_progress') {
    return 'status-busy';
  }
  if (s === 'idle' || s === 'stop') {
    return 'status-idle';
  }
  return 'status-active';
}

// Poll the server for latest rover positions every 5 seconds
async function fetchPositions() {
  try {
    const res = await fetch('/get_positions');
    if (!res.ok) return;
    const data = await res.json();

    // map by rover_id for quick lookup
    const map = {};
    data.forEach(item => { map[item.rover_id] = item; });

    // if modal open, skip updating to avoid interrupting user
    const modal = document.getElementById('formModal');
    if (modal && modal.classList.contains('show')) return;

    // Live Deliveries table rows only (skip history table)
    const liveRows = document.querySelectorAll('.table-container:not(.history) tbody tr');
    liveRows.forEach((row) => {
      const idText = row.cells?.[0]?.innerText || '';
      const rid = parseInt(idText.trim(), 10);
      if (!Number.isFinite(rid)) return;

      const statusCell = row.cells?.[1];
      const aisleCell = row.cells?.[2];
      const tableCell = row.cells?.[3];
      if (!statusCell || !aisleCell || !tableCell) return;

      const pos = map[rid];
      if (pos) {
        const dotClass = getStatusDotClass(pos.status);
        statusCell.innerHTML = `<span class="status-dot ${dotClass}"></span> ${pos.status}`;
        aisleCell.textContent = pos.lat;
        tableCell.textContent = pos.lon;
        tableCell.classList.remove('placeholder');
      } else {
        statusCell.innerHTML = '<span class="status-dot status-idle"></span> Idle';
        aisleCell.textContent = '-';
        tableCell.textContent = '-';
        tableCell.classList.add('placeholder');
      }
    });
  } catch (err) {
    // silently ignore errors; could add console.log(err) for debugging
  }
}

// start polling immediately and then every 5s
fetchPositions();
if (pollInterval) clearInterval(pollInterval);
pollInterval = setInterval(fetchPositions, 5000);
