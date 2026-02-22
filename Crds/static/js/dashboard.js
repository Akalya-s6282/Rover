let pollInterval = null;

function toggleForm() {
  const modal = document.getElementById("formModal");
  if (!modal) return;
  modal.classList.toggle("show");
}

window.addEventListener("click", (event) => {
  const modal = document.getElementById("formModal");
  if (modal && event.target === modal) {
    modal.classList.remove("show");
  }
});

function buildGpioInputs() {
  const totalInput = document.querySelector('input[name="total_latitudes"]');
  if (!totalInput) return;

  const total = parseInt(totalInput.value, 10);
  if (!total || total <= 0) {
    alert("Enter a positive number for total latitudes");
    return;
  }

  const container = document.getElementById("gpioInputsContainer");
  if (!container) return;
  container.innerHTML = "";

  for (let i = 1; i <= total; i++) {
    const row = document.createElement("div");
    row.className = "gpio-row";

    const label = document.createElement("label");
    label.innerText = `Aile ${i}:`;

    const hiddenIndex = document.createElement("input");
    hiddenIndex.type = "hidden";
    hiddenIndex.name = "latitude_index";
    hiddenIndex.value = i;

    const gpioInput = document.createElement("input");
    gpioInput.type = "number";
    gpioInput.name = "gpio_pin";
    gpioInput.placeholder = "GPIO pin number";
    gpioInput.required = true;

    row.appendChild(label);
    row.appendChild(hiddenIndex);
    row.appendChild(gpioInput);
    container.appendChild(row);
  }

  const gpioSection = document.getElementById("gpioSection");
  if (gpioSection) gpioSection.style.display = "block";

  const totalLatHidden = document.getElementById("totalLatHidden");
  if (totalLatHidden) totalLatHidden.value = total;

  const notice = document.getElementById("gpioSavedNotice");
  if (notice) notice.style.display = "block";
}

function getStatusDotClass(statusValue) {
  const s = String(statusValue || "").toLowerCase();
  if (s.includes("busy") || s.includes("transit") || s === "delivering" || s === "in_progress") {
    return "status-busy";
  }
  if (s === "idle" || s === "stop") {
    return "status-idle";
  }
  return "status-active";
}

function renderLiveDeliveries(rows) {
  const body = document.getElementById("liveDeliveriesBody");
  if (!body) return;

  if (!Array.isArray(rows) || rows.length === 0) {
    body.innerHTML = '<tr><td colspan="5">No rovers yet.</td></tr>';
    return;
  }

  const html = rows.map((row) => {
    const roverId = Number(row.rover_id);
    const status = row.status || "idle";
    const dotClass = getStatusDotClass(status);
    const lat = (row.lat === null || row.lat === undefined) ? "-" : row.lat;
    const lon = (row.lon === null || row.lon === undefined) ? "-" : row.lon;

    return `
      <tr>
        <td><strong>${roverId}</strong></td>
        <td><span class="status-dot ${dotClass}"></span> ${status}</td>
        <td>${lat}</td>
        <td class="col-center ${lon === "-" ? "placeholder" : ""}">${lon}</td>
        <td class="col-action">
          <div class="action-group">
            <a class="btn-action link" href="/asssign/${roverId}">Assign</a>
            <form action="/delete/${roverId}" method="post" class="delete-form">
              <button type="submit" class="btn-icon" title="Delete">Delete</button>
            </form>
          </div>
        </td>
      </tr>
    `;
  }).join("");

  body.innerHTML = html;
}

function renderOrderHistory(rows) {
  const body = document.getElementById("orderHistoryBody");
  if (!body) return;

  if (!Array.isArray(rows) || rows.length === 0) {
    body.innerHTML = '<tr><td colspan="4">No deliveries yet.</td></tr>';
    return;
  }

  const html = rows.map((row) => `
    <tr>
      <td><strong>${row.rover_id}</strong></td>
      <td>${row.status || "-"}</td>
      <td>${row.started || "-"}</td>
      <td>${row.completed || "-"}</td>
    </tr>
  `).join("");

  body.innerHTML = html;
}

function updateLiveMetrics(data) {
  const hotel = document.getElementById("hotelNameValue");
  const shift = document.getElementById("shiftValue");
  const time = document.getElementById("timeValue");
  const active = document.getElementById("activeRoversValue");
  const today = document.getElementById("deliveriesTodayValue");
  const avg = document.getElementById("avgDeliveryTimeValue");

  if (hotel) hotel.textContent = data.hotel_name || "-";
  if (shift) shift.textContent = data.shift || "-";
  if (time) time.textContent = data.current_time || "-";
  if (active) active.textContent = `${data.active_rovers ?? 0}/${data.total_rovers ?? 0}`;
  if (today) today.textContent = `${data.deliveries_today ?? 0}`;
  if (avg) avg.textContent = data.avg_delivery_time || "-";
}

async function fetchDashboardLive() {
  try {
    const res = await fetch("/dashboard/live");
    if (!res.ok) return;

    const data = await res.json();
    if (!data || !data.ok) return;

    const modal = document.getElementById("formModal");
    if (modal && modal.classList.contains("show")) return;

    updateLiveMetrics(data);
    renderLiveDeliveries(data.live_deliveries || []);
    renderOrderHistory(data.order_history || []);
  } catch (err) {
    // no-op
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const gpioBtn = document.getElementById("showGpioBtn");
  if (gpioBtn) gpioBtn.addEventListener("click", buildGpioInputs);

  if (document.getElementById("liveDeliveriesBody")) {
    fetchDashboardLive();
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(fetchDashboardLive, 5000);
  }
});
