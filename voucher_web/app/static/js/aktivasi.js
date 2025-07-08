let installationCheckInterval;
let isInstallationComplete = false;
let downloadStarted = false;

// Lock internet saat tab ditutup
window.addEventListener('beforeunload', (e) => {
  const clientMac = document.getElementById("clientMac")?.value;
  if (clientMac) {
    navigator.sendBeacon('/lock-internet', JSON.stringify({ mac: clientMac }));
  }
});

function getUrlParameter(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  const regex = new RegExp("[\\?&]" + name + "=([^&#]*)");
  const results = regex.exec(location.search);
  return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

// Countdown internet usage
function startCountdown(durationSeconds, macAddress) {
  let timeLeft = durationSeconds;
  const hoursElement = document.getElementById("hours");
  const minutesElement = document.getElementById("minutes");
  const secondsElement = document.getElementById("seconds");

  function updateCountdownDisplay(time) {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = time % 60;
    if (hoursElement) hoursElement.innerHTML = hours.toString().padStart(2, '0');
    if (minutesElement) minutesElement.innerHTML = minutes.toString().padStart(2, '0');
    if (secondsElement) secondsElement.innerHTML = seconds.toString().padStart(2, '0');
  }

  updateCountdownDisplay(timeLeft);

  const interval = setInterval(() => {
    if (timeLeft <= 0) {
      clearInterval(interval);
      updateCountdownDisplay(0);
      lockInternet(macAddress);
      return;
    }

    timeLeft--;
    updateCountdownDisplay(timeLeft);
  }, 1000);
}

// Kirim permintaan lock internet ke server
async function lockInternet(macAddress) {
  try {
    const response = await fetch("/lock-internet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mac: macAddress })
    });

    const result = await response.json();
    if (response.ok) {
      alert("Waktu habis. Internet telah dikunci.");
      console.log("Internet locked:", result);
    } else {
      throw new Error(result.message || "Locking failed");
    }
  } catch (error) {
    console.error("Error locking internet:", error);
  }
}

// Deteksi MAC dari hidden field atau fallback
function getMacAddress() {
  const macInput = document.getElementById("clientMac");
  return macInput?.value?.trim() || null;
}

// Validasi format MAC address
function isValidMac(mac) {
  return /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/.test(mac);
}

// Fungsi untuk memulai aktivasi
async function activateVoucher(voucherCode, macAddress) {
  try {
    const response = await fetch("/validate-voucher", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ voucher_code: voucherCode, mac: macAddress })
    });

    const result = await response.json();
    if (result.valid) {
      console.log("[INFO] Voucher valid, internet dibuka");

      document.getElementById("voucherForm").classList.add("hidden");
      document.getElementById("generateBtn").classList.add("hidden");
      document.getElementById("installStatus").classList.add("hidden");
      document.getElementById("filenameDisplay").classList.add("hidden");
      document.getElementById("activatedSection").classList.remove("hidden");
      document.getElementById("countdownSection").classList.remove("hidden");

      generateTransactionId();
      setCurrentTime();

      const serviceId = getUrlParameter("service") || "basic";
      getPackageInfo(serviceId, macAddress);
    } else {
      showError(result.message || "Voucher tidak valid");
    }
  } catch (err) {
    console.error("Validasi gagal:", err);
    showError("Terjadi kesalahan sistem.");
  }
}

// Tampilkan error
function showError(message) {
  const errorElement = document.getElementById("voucherError");
  errorElement.textContent = message;
  errorElement.classList.add("visible");
}

// ID Transaksi
function generateTransactionId() {
  const chars = "0123456789";
  let txId = "TRX-";
  for (let i = 0; i < 8; i++) {
    txId += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  document.getElementById("transactionId").textContent = txId;
}

// Waktu aktivasi
function setCurrentTime() {
  const now = new Date();
  const formatted = now.toLocaleString("id-ID", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit"
  });
  document.getElementById("activationTime").textContent = formatted;
}

// Ambil info paket berdasarkan URL param
function getPackageInfo(serviceId, macAddress) {
  fetch(`/get-package-info?service=${serviceId}`)
    .then(res => res.json())
    .then(data => {
      document.getElementById("packageName").textContent = `${data.name} ${data.duration}`;
      document.getElementById("packageSpeed").textContent = data.speed;
      startCountdown(data.duration_seconds, macAddress);
    })
    .catch(() => {
      document.getElementById("packageName").textContent = "Standar 1 Jam";
      document.getElementById("packageSpeed").textContent = "10 Mbps";
      startCountdown(3600, macAddress);
    });
}

// Proses submit voucher
document.getElementById("voucherForm").addEventListener("submit", async function (e) {
  e.preventDefault();
  const voucherCode = document.getElementById("voucherCode").value.trim();
  const mac = getMacAddress();

  if (!voucherCode) {
    showError("Kode voucher harus diisi");
    return;
  }

  if (!isValidMac(mac)) {
    showError("Perangkat tidak dikenali. Hubungi petugas.");
    return;
  }

  await activateVoucher(voucherCode, mac);
});

// Tombol download app
document.getElementById("generateBtn").addEventListener("click", function () {
  if (isInstallationComplete) return;

  const btn = this;
  const installStatus = document.getElementById("installStatus");

  btn.classList.add("btn-disabled");
  btn.disabled = true;
  downloadStarted = true;
  installStatus.classList.remove("hidden");

  fetch("/download-voucher-app", { method: "HEAD" })
    .then(res => {
      if (!res.ok) throw new Error("File tidak ditemukan");
      startDownload();
    })
    .catch(err => {
      alert("File tidak tersedia: " + err.message);
      resetGenerateButton();
    });

  function startDownload() {
    const a = document.createElement("a");
    a.href = "/download-voucher-app";
    a.download = "VoucherApp.exe";
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    setTimeout(() => document.body.removeChild(a), 1000);
    startInstallationCheck();
  }

  function startInstallationCheck() {
    setTimeout(() => checkInstallationStatus(), 2000);
    installationCheckInterval = setInterval(() => {
      if (!isInstallationComplete) checkInstallationStatus();
    }, 3000);
    setTimeout(() => {
      if (!isInstallationComplete) onInstallationComplete();
    }, 15000);
  }
});

// Pengecekan status instalasi (simulasi)
function checkInstallationStatus() {
  fetch("/check-installation-status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ check_type: "voucher_app" })
  })
    .then(res => res.json())
    .then(data => {
      if (data.installed) onInstallationComplete();
    })
    .catch(() => {
      setTimeout(() => onInstallationComplete(), 10000);
    });
}

function onInstallationComplete() {
  if (isInstallationComplete) return;
  isInstallationComplete = true;
  clearInterval(installationCheckInterval);

  const installStatus = document.getElementById("installStatus");
  const filenameDisplay = document.getElementById("filenameDisplay");

  installStatus.innerHTML = `
    <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#155724" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
      <span>Instalasi berhasil!</span>
    </div>`;
  installStatus.classList.add("success");

  filenameDisplay.textContent = `Voucher berhasil dibuat. Klik untuk membuka dan aktifkan.`;
  filenameDisplay.classList.remove("hidden");

  resetGenerateButton();
}

function resetGenerateButton() {
  const btn = document.getElementById("generateBtn");
  btn.classList.remove("btn-disabled");
  btn.disabled = false;
  downloadStarted = false;
  document.getElementById("installStatus").classList.add("hidden");
}
