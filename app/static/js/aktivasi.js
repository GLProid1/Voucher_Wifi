let installationCheckInterval;
let isInstallationComplete = false;
let downloadStarted = false;

function getUrlParameter(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)");
  var results = regex.exec(location.search);
  return results === null
    ? ""
    : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function startCountdown(durationSeconds) {
  let timeLeft = durationSeconds;
  const hoursElement = document.getElementById("hours");
  const minutesElement = document.getElementById("minutes");
  const secondsElement = document.getElementById("seconds");

  updateCountdownDisplay(timeLeft);

  const interval = setInterval(() => {
    if (timeLeft <= 0) {
      clearInterval(interval);
      hoursElement.innerHTML = "00";
      minutesElement.innerHTML = "00";
      secondsElement.innerHTML = "00";
      alert("Waktu penggunaan internet Anda telah habis.");
      return;
    }

    timeLeft--;
    updateCountdownDisplay(timeLeft);
  }, 1000);

  function updateCountdownDisplay(time) {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = time % 60;

    hoursElement.innerHTML = hours < 10 ? "0" + hours : hours;
    minutesElement.innerHTML = minutes < 10 ? "0" + minutes : minutes;
    secondsElement.innerHTML = seconds < 10 ? "0" + seconds : seconds;
  }
}

function generateTransactionId() {
  const chars = "0123456789";
  const prefix = "TRX-";
  let txId = "";

  for (let i = 0; i < 8; i++) {
    txId += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  document.getElementById("transactionId").textContent = prefix + txId;
}

function setCurrentTime() {
  const now = new Date();
  const day = String(now.getDate()).padStart(2, "0");
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const year = now.getFullYear();
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");

  const formattedTime = `${day}/${month}/${year} ${hours}:${minutes}`;
  document.getElementById("activationTime").textContent = formattedTime;
}

function getPackageInfo(serviceId) {
  fetch(`/get-package-info?service=${serviceId}`)
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("packageName").textContent =
        data.name + " " + data.duration;
      document.getElementById("packageSpeed").textContent = data.speed;
      startCountdown(data.duration_seconds);
    })
    .catch((error) => {
      document.getElementById("packageName").textContent = "Standar 1 Jam";
      document.getElementById("packageSpeed").textContent = "10 Mbps";
      startCountdown(3600);
    });
}

// Fungsi untuk memeriksa status instalasi
function checkInstallationStatus() {
  // Jika download tidak dimulai, reset tombol
  if (!downloadStarted) {
    resetGenerateButton();
    return;
  }

  // Simulasi pengecekan instalasi
  fetch("/check-installation-status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ check_type: "voucher_app" }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.installed) {
        onInstallationComplete();
      }
    })
    .catch(() => {
      // Fallback: gunakan simulasi waktu jika server tidak mendukung
      setTimeout(() => {
        onInstallationComplete();
      }, 10000);
    });
}

// Fungsi yang dipanggil ketika instalasi selesai
function onInstallationComplete() {
  if (isInstallationComplete) return;

  isInstallationComplete = true;
  clearInterval(installationCheckInterval);

  const installStatus = document.getElementById("installStatus");
  const filenameDisplay = document.getElementById("filenameDisplay");

  // Update status instalasi
  installStatus.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#155724" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <span>Instalasi berhasil!</span>
      </div>
    `;
  installStatus.classList.add("success");

  // Tampilkan pesan aktivasi
  filenameDisplay.textContent = `Voucher berhasil dibuat. Klik untuk membuka dan aktifkan.`;
  filenameDisplay.classList.remove("hidden");

  // Re-enable tombol generate jika diperlukan
  resetGenerateButton();
}

// Fungsi untuk mereset tombol generate
function resetGenerateButton() {
  const generateBtn = document.getElementById("generateBtn");
  generateBtn.classList.remove("btn-disabled");
  generateBtn.disabled = false;
  downloadStarted = false;

  const installStatus = document.getElementById("installStatus");
  installStatus.classList.add("hidden");
}

document.getElementById("voucherForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const voucherCode = document.getElementById("voucherCode").value.trim();
  const errorElement = document.getElementById("voucherError");

  if (!voucherCode) {
    errorElement.textContent = "Kode voucher harus diisi";
    errorElement.classList.add("visible");
    return;
  }

  // Validasi ke server Flask
  fetch("/validate-voucher", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ voucher_code: voucherCode }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.valid) {
        errorElement.classList.remove("visible");
        document.getElementById("voucherForm").classList.add("hidden");
        document.getElementById("generateBtn").classList.add("hidden");
        document.getElementById("installStatus").classList.add("hidden");
        document.getElementById("filenameDisplay").classList.add("hidden");
        document.getElementById("activatedSection").classList.remove("hidden");
        document.getElementById("countdownSection").classList.remove("hidden");

        generateTransactionId();
        setCurrentTime();

        const serviceId = getUrlParameter("service") || "basic";
        getPackageInfo(serviceId);

        fetch("/unlock-internet", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.status === "success") {
              console.log("Internet unlocked successfully");
            } else {
              console.error("Failed to unlock internet:", data.message);
            }
          })
          .catch((error) => {
            console.error("Error unlocking internet:", error);
          });
      } else {
        errorElement.textContent =
          "Kode voucher tidak valid atau sudah digunakan";
        errorElement.classList.add("visible");
      }
    })
    .catch(() => {
      errorElement.textContent =
        "Gagal memvalidasi voucher. Silakan coba lagi.";
      errorElement.classList.add("visible");
    });
});

// Perbaikan untuk bagian download di aktivasi.js

document.getElementById("generateBtn").addEventListener("click", function () {
  if (isInstallationComplete) return;

  const generateBtn = this;
  const installStatus = document.getElementById("installStatus");

  // Disable tombol dan tampilkan status instalasi
  generateBtn.classList.add("btn-disabled");
  generateBtn.disabled = true;
  installStatus.classList.remove("hidden");
  downloadStarted = true;

  // Cek ketersediaan file terlebih dahulu
  fetch("/download-voucher-app", { method: "HEAD" })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      // Jika file tersedia, lakukan download
      startDownload();
    })
    .catch((error) => {
      console.error("Download failed:", error);
      alert("File voucher belum tersedia atau terjadi kesalahan.");
      resetGenerateButton();
      return;
    });

  function startDownload() {
    try {
      // Buat link download
      const a = document.createElement("a");
      a.href = "/download-voucher-app";
      a.download = "VoucherApp.exe";
      a.style.display = "none";

      // Tambahkan ke DOM dan trigger download
      document.body.appendChild(a);
      a.click();

      // Bersihkan setelah download
      setTimeout(() => {
        if (document.body.contains(a)) {
          document.body.removeChild(a);
        }
      }, 1000);

      // Mulai pengecekan instalasi
      startInstallationCheck();
    } catch (error) {
      console.error("Error creating download:", error);
      alert("Gagal memulai download. Silakan coba lagi.");
      resetGenerateButton();
    }
  }

  function startInstallationCheck() {
    // Mulai pengecekan instalasi setelah delay
    setTimeout(() => {
      checkInstallationStatus();
    }, 2000);

    // Set interval untuk pengecekan berkala
    installationCheckInterval = setInterval(() => {
      if (!isInstallationComplete) {
        checkInstallationStatus();
      }
    }, 3000);

    // Auto-complete setelah 15 detik jika tidak ada response
    setTimeout(() => {
      if (!isInstallationComplete) {
        onInstallationComplete();
      }
    }, 15000);
  }
});

// Fungsi untuk debug - tambahkan ini untuk troubleshooting
function debugDownload() {
  fetch("/download-voucher-app", { method: "HEAD" })
    .then((res) => {
      console.log("Download URL Status:", res.status);
      console.log("Response Headers:", res.headers);
      return res;
    })
    .then((res) => {
      if (res.ok) {
        console.log("File tersedia untuk download");
      } else {
        console.log("File tidak tersedia:", res.statusText);
      }
    })
    .catch((error) => {
      console.error("Error checking download:", error);
    });
}
