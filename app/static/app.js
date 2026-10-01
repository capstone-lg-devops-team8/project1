// =============================================================================
// 전역 변수
// =============================================================================
let subscribers = [];
let currentDevices = [];
let selectedUserId = null;
let selectedDeviceId = null;
let usageChart = null;


// =============================================================================
// 헬퍼
// =============================================================================
function show(el, display = "block") {
    el.classList.remove("hidden");
    el.style.display = display;
}
function hide(el) {
    el.style.display = "none";
}
function isAll(filter) {
    return !filter || filter.toLowerCase() === "all";
}


// =============================================================================
// [요구사항 #3] 상태 기반 Badge 스타일
// =============================================================================
function badgeClass(value) {
    const v = (value || "").toLowerCase();

    if (["active", "online", "normal"].includes(v)) return "badge status-active";
    if (["paused", "standby"].includes(v)) return "badge status-paused";
    if (["expired", "error", "warning"].includes(v)) return "badge status-expired";
    if (v === "offline") return "badge status-offline";
    if (["on", "cleaning"].includes(v)) return "badge status-on";
    if (v === "off") return "badge status-off";
    return "badge";
}


// =============================================================================
// [요구사항 #1] 구독 사용자 조회 + 검색/필터
// =============================================================================
async function fetchSubscribers() {
    try {
        const res = await fetch("/api/subscribers");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        subscribers = await res.json();
        renderSubscribers();
    } catch (err) {
        console.error("구독자 조회 실패:", err);
    }
}

function renderSubscribers() {
    const tbody = document.getElementById("subscriber-body");
    const search = document.getElementById("subscriber-search").value.toLowerCase();
    const statusFilter = document.getElementById("subscriber-status-filter").value;

    const filtered = subscribers.filter((s) => {
        const matchSearch = [s.name, s.plan, s.status, s.userId]
            .some((f) => String(f ?? "").toLowerCase().includes(search));
        const matchStatus = isAll(statusFilter)
            || String(s.status).toLowerCase() === statusFilter.toLowerCase();
        return matchSearch && matchStatus;
    });

    tbody.innerHTML = "";
    filtered.forEach((s) => {
        const tr = document.createElement("tr");
        if (s.userId === selectedUserId) tr.classList.add("selected");
        tr.innerHTML = `
            <td>${s.userId}</td>
            <td>${s.name}</td>
            <td>${s.plan}</td>
            <td><span class="${badgeClass(s.status)}">${s.status}</span></td>
            <td>${s.deviceCount}</td>
        `;
        tr.addEventListener("click", () => selectSubscriber(s.userId));
        tbody.appendChild(tr);
    });
}


// =============================================================================
// [요구사항 #2] 사용자별 가전 목록 + 사용 현황 + 차트
// =============================================================================
async function selectSubscriber(userId) {
    selectedUserId = userId;
    selectedDeviceId = null;
    renderSubscribers();

    show(document.getElementById("usage-empty"));
    hide(document.getElementById("usage-detail"));
    document.getElementById("usage-info").innerHTML = "";

    try {
        const res = await fetch(`/api/subscribers/${userId}/devices`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        currentDevices = await res.json();
    } catch (err) {
        console.error("가전 목록 조회 실패:", err);
        currentDevices = [];
    }
    renderDevices();
}

function renderDevices() {
    const emptyEl = document.getElementById("device-empty");
    const tableEl = document.getElementById("device-table");
    const tbody = document.getElementById("device-body");
    const search = document.getElementById("device-search").value.toLowerCase();
    const statusFilter = document.getElementById("device-status-filter").value;

    const filtered = currentDevices.filter((d) => {
        const matchSearch = [d.type, d.model, d.status, d.deviceId, d.location]
            .some((f) => String(f ?? "").toLowerCase().includes(search));
        const matchStatus = isAll(statusFilter)
            || String(d.status).toLowerCase() === statusFilter.toLowerCase();
        return matchSearch && matchStatus;
    });

    tbody.innerHTML = "";

    if (currentDevices.length === 0) {
        emptyEl.textContent = "No registered devices";
        show(emptyEl);
        hide(tableEl);
        return;
    }
    if (filtered.length === 0) {
        emptyEl.textContent = "No devices matched";
        show(emptyEl);
        hide(tableEl);
        return;
    }

    hide(emptyEl);
    show(tableEl, "table");

    filtered.forEach((d) => {
        const tr = document.createElement("tr");
        if (d.deviceId === selectedDeviceId) tr.classList.add("selected");
        tr.innerHTML = `
            <td>${d.deviceId}</td>
            <td>${d.type}</td>
            <td>${d.model}</td>
            <td>${d.location}</td>
            <td><span class="${badgeClass(d.status)}">${d.status}</span></td>
        `;
        tr.addEventListener("click", () => selectDevice(d.deviceId));
        tbody.appendChild(tr);
    });
}

async function selectDevice(deviceId) {
    selectedDeviceId = deviceId;
    renderDevices();

    let data;
    try {
        const res = await fetch(`/api/devices/${deviceId}/usage`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        data = await res.json();
    } catch (err) {
        console.error("사용 현황 조회 실패:", err);
        return;
    }

    hide(document.getElementById("usage-empty"));
    show(document.getElementById("usage-detail"));

    document.getElementById("usage-info").innerHTML = `
        <div class="label">Device ID</div><div class="value">${data.deviceId}</div>
        <div class="label">Device Name</div><div class="value">${data.deviceName ?? "-"}</div>
        <div class="label">Power Status</div><div class="value"><span class="${badgeClass(data.powerStatus)}">${data.powerStatus ?? "-"}</span></div>
        <div class="label">Last Used</div><div class="value">${data.lastUsedAt ?? "-"}</div>
        <div class="label">Total Usage Hours</div><div class="value">${data.totalUsageHours ?? "-"}</div>
        <div class="label">Weekly Usage Count</div><div class="value">${data.weeklyUsageCount ?? "-"}</div>
        <div class="label">Health Status</div><div class="value"><span class="${badgeClass(data.healthStatus)}">${data.healthStatus ?? "-"}</span></div>
        <div class="label">Remark</div><div class="value">${data.remark ?? "-"}</div>
    `;

    renderUsageChart(data.weeklyUsageTrend || []);
}

function renderUsageChart(trend) {
    const ctx = document.getElementById("usageChart");

    if (usageChart) usageChart.destroy();

    usageChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            datasets: [{
                label: "Weekly Usage Trend",
                data: trend,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}


// =============================================================================
// 이벤트 바인딩 + 초기화
// =============================================================================
function bindEvents() {
    document.getElementById("subscriber-search").addEventListener("input", renderSubscribers);
    document.getElementById("subscriber-status-filter").addEventListener("change", renderSubscribers);

    document.getElementById("device-search").addEventListener("input", renderDevices);
    document.getElementById("device-status-filter").addEventListener("change", renderDevices);
}

bindEvents();
fetchSubscribers();