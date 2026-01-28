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

