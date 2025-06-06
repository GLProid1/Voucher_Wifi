// Inisialisasi peta
let map = L.map("map").setView([1.106, 103.9761], 18);
let markers = [];
let currentLocationMarker = null;
let currentLocationCircle = null;

// Tambahkan tile layer (OpenStreetMap)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// Tambahkan kontrol lokasi saat ini
L.control
  .locate({
    position: "bottomright",
    drawCircle: true,
    follow: true,
    setView: true,
    keepCurrentZoomLevel: true,
    markerStyle: {
      weight: 1,
      opacity: 0.8,
      fillOpacity: 0.8,
    },
    circleStyle: {
      weight: 1,
      clickable: false,
    },
    icon: "fas fa-location-arrow",
    metric: true,
    strings: {
      title: "Lokasi saya saat ini",
      popup: "Anda berada dalam radius {distance} {unit} dari titik ini",
      outsideMapBoundsMsg: "Anda berada di luar area peta",
    },
    locateOptions: {
      maxZoom: 18,
      watch: true,
      enableHighAccuracy: true,
      maximumAge: 10000,
      timeout: 10000,
    },
  })
  .addTo(map);

// Variabel untuk menyimpan data
let allLocationData = [];

// Fungsi untuk memuat data
async function loadData(showLoading = false) {
  if (showLoading) {
    document.getElementById("loadingIndicator").style.display = "flex";
    document.getElementById("refreshIcon").classList.add("rotate-animation");
  }

  try {
    const response = await fetch("/get-location-data");
    const data = await response.json();

    // Simpan data
    allLocationData = data.entries;

    // Update statistik
    document.getElementById("total-access").textContent = data.total_entries;
    document.getElementById("today-access").textContent = data.today_entries;
    document.getElementById("best-accuracy").textContent =
      data.best_accuracy + " m";
    document.getElementById("avg-accuracy").textContent =
      data.avg_accuracy + " m";

    // Update peta
    updateMap(data.entries);

    // Update tabel dengan data terbaru di atas
    updateTable(data.entries);

    // Tampilkan pesan jika tidak ada data
    if (data.entries.length === 0) {
      document.getElementById("noData").style.display = "block";
      document.getElementById("dataTable").style.display = "none";
    } else {
      document.getElementById("noData").style.display = "none";
      document.getElementById("dataTable").style.display = "table";
    }
  } catch (error) {
    console.error("Gagal memuat data:", error);
    alert("Gagal memuat data. Silakan coba lagi.");
  } finally {
    document.getElementById("loadingIndicator").style.display = "none";
    setTimeout(() => {
      document
        .getElementById("refreshIcon")
        .classList.remove("rotate-animation");
    }, 500);
  }
}

// Fungsi untuk memperbarui peta
function updateMap(entries) {
  // Hapus semua marker yang ada
  markers.forEach((marker) => map.removeLayer(marker));
  markers = [];

  if (entries.length === 0) return;

  // Buat array untuk menyimpan semua koordinat
  const allLatLngs = [];

  // Buat marker untuk setiap entri
  entries.forEach((entry, index) => {
    const lat = parseFloat(entry.latitude);
    const lng = parseFloat(entry.longitude);
    const latLng = [lat, lng];
    allLatLngs.push(latLng);

    // Warna marker berdasarkan akurasi
    let markerColor =
      entry.accuracy < 50 ? "green" : entry.accuracy < 100 ? "orange" : "red";

    // Buat marker
    const marker = L.circleMarker(latLng, {
      radius: 8,
      fillColor: markerColor,
      color: "#fff",
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8,
    }).addTo(map);

    // Tambahkan popup
    marker.bindPopup(`
          <b>Waktu:</b> ${entry.timestamp}<br>
          <b>Koordinat:</b> ${lat}, ${lng}<br>
          <b>Akurasi:</b> ${entry.accuracy} m
        `);

    // Jika ini marker terbaru (index 0), buat lebih menonjol
    if (index === 0) {
      marker.setStyle({
        radius: 12,
        weight: 3,
      });

      // Buat lingkaran akurasi untuk marker terbaru
      const accuracyCircle = L.circle(latLng, {
        radius: entry.accuracy,
        fillColor: "#3388ff",
        fillOpacity: 0.1,
        color: "#3388ff",
        weight: 1,
      }).addTo(map);

      markers.push(accuracyCircle);
    }

    markers.push(marker);
  });

  // Sesuaikan view peta untuk menampilkan semua marker
  if (allLatLngs.length > 0) {
    const bounds = L.latLngBounds(allLatLngs);
    map.fitBounds(bounds, { padding: [50, 50] });
  }
}

// Fungsi untuk memperbarui tabel
function updateTable(entries) {
  const tableBody = document.getElementById("data-table-body");
  tableBody.innerHTML = "";

  // Membalikkan urutan array sehingga yang terbaru muncul pertama
  const reversedEntries = [...entries].reverse();

  reversedEntries.forEach((entry, index) => {
    const row = document.createElement("tr");

    // Format timestamp
    const timestampCell = document.createElement("td");
    timestampCell.innerHTML = `<div class="timestamp">${entry.timestamp}</div>`;

    // Format lokasi
    const locationCell = document.createElement("td");
    locationCell.textContent = `${entry.latitude}, ${entry.longitude}`;

    // Format akurasi
    const accuracyCell = document.createElement("td");
    const accuracyClass =
      entry.accuracy < 50
        ? "high-accuracy"
        : entry.accuracy < 100
        ? "medium-accuracy"
        : "low-accuracy";
    accuracyCell.innerHTML = `<span class="accuracy ${accuracyClass}">${entry.accuracy} m</span>`;

    // Format aksi
    const actionCell = document.createElement("td");
    actionCell.className = "action-cell";
    actionCell.innerHTML = `
          <a href="${
            entry.maps_link
          }" target="_blank" class="btn-icon view" title="Lihat di Google Maps">
            <i class="fas fa-map-marker-alt"></i>
          </a>
          <button class="btn-icon info" onclick="showInfoModal(${
            entries.length - 1 - index
          })" title="Lihat informasi detail">
            <i class="fas fa-info"></i>
          </button>
        `;

    row.appendChild(timestampCell);
    row.appendChild(locationCell);
    row.appendChild(accuracyCell);
    row.appendChild(actionCell);

    tableBody.appendChild(row);
  });
}

// Fungsi untuk menampilkan modal informasi
function showInfoModal(index) {
  const entry = allLocationData[index];
  const infoModalBody = document.getElementById("infoModalBody");

  // Format tanggal dan waktu lebih manusiawi
  const timestamp = new Date(entry.timestamp.replace(/-/g, "/"));
  const formattedDate = timestamp.toLocaleDateString("id-ID", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  const formattedTime = timestamp.toLocaleTimeString("id-ID");

  infoModalBody.innerHTML = `
        <div class="info-item">
          <div class="info-label">Tanggal</div>
          <div class="info-value">${formattedDate}</div>
        </div>
        <div class="info-item">
          <div class="info-label">Waktu</div>
          <div class="info-value">${formattedTime}</div>
        </div>
        <div class="info-item">
          <div class="info-label">Latitude</div>
          <div class="info-value">${entry.latitude}</div>
        </div>
        <div class="info-item">
          <div class="info-label">Longitude</div>
          <div class="info-value">${entry.longitude}</div>
        </div>
        <div class="info-item">
          <div class="info-label">Akurasi</div>
          <div class="info-value">${entry.accuracy} meter</div>
        </div>
        <div class="info-item">
          <div class="info-label">Link Google Maps</div>
          <div class="info-value">
            <a href="${entry.maps_link}" target="_blank" class="map-link">Buka di Google Maps</a>
          </div>
        </div>
      `;

  document.getElementById("infoModal").style.display = "flex";
}

function closeInfoModal() {
  document.getElementById("infoModal").style.display = "none";
}

// Muat data saat halaman pertama kali dimuat
document.addEventListener("DOMContentLoaded", () => loadData(true));

// Atur ulang ukuran peta saat jendela diubah ukurannya
window.addEventListener("resize", () => {
  map.invalidateSize();
});
