let selectedService = null;

function selectService(element, serviceId) {
  // Jika kotak yang sama diklik (sudah terpilih), batalkan pilihan
  if (element.classList.contains("selected")) {
    element.classList.remove("selected");
    selectedService = null;
    document.getElementById("continueBtn").disabled = true;
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
}

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
}

function getLocation(button) {
  const errorBox = document.getElementById("errorMsg");
  button.disabled = true;
  button.classList.add("loading");
  errorBox.textContent = "";
  errorBox.classList.remove("visible");

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        const accuracy = pos.coords.accuracy;

        // Validasi lokasi
        if (accuracy > 5000) {
          errorBox.textContent =
            "Lokasi tidak cukup akurat (akurasi: " +
            Math.round(accuracy) +
            "m). Mohon aktifkan GPS dan coba lagi.";
          errorBox.classList.add("visible");
          button.disabled = false;
          button.classList.remove("loading");
          return;
        }

        if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
          errorBox.textContent = "Lokasi tidak valid. Mohon coba lagi.";
          errorBox.classList.add("visible");
          button.disabled = false;
          button.classList.remove("loading");
          return;
        }

        // Kirim ke server dengan error handling
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
      },
      (err) => {
        let errorMessage = "Gagal mengambil lokasi. Coba lagi ya.";
        if (err.code === err.PERMISSION_DENIED) {
          errorMessage = "Akses lokasi ditolak. Mohon izinkan akses lokasi.";
        } else if (err.code === err.TIMEOUT) {
          errorMessage = "Waktu permintaan lokasi habis. Coba lagi ya.";
        }
        errorBox.textContent = errorMessage;
        errorBox.classList.add("visible");
        button.disabled = false;
        button.classList.remove("loading");
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  } else {
    errorBox.textContent = "Browser kamu nggak support geolokasi.";
    errorBox.classList.add("visible");
    button.disabled = false;
    button.classList.remove("loading");
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
