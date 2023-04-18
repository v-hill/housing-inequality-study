// Define the stationData variable in the global scope
let stationData = null;

$(document).ready(function () {
    // Create the map
    const map = L.map('map');
    const boundary_id = getBoundaryId();

    // Define the colors for the markers
    const GREEN_ICON = L.icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    const RED_ICON = L.icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    // Add a tile layer to the map
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    $.ajax({
        url: `stations?boundary_id=${boundary_id}`,
        type: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        success: function (data) {
            stationData = data;
            addStationsToMap(stationData, GREEN_ICON, RED_ICON, map);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error("Ajax request failed to fetch train stations map data: " + textStatus + ", " + errorThrown);
            console.log("Response status: " + jqXHR.status);
        }
    });

    // Get a reference to the show boundary stations toggle element
    const showBoundaryStationsToggle = document.getElementById('show-boundary-stations-toggle');
    // Add an event listener to the toggle element
    showBoundaryStationsToggle.addEventListener('change', function () {
        // Fetch train station data from the Django view
        addStationsToMap(stationData, GREEN_ICON, RED_ICON, map);
    });




});

function addStationsToMap(stationData, GREEN_ICON, RED_ICON, map) {
    let latSum = 0;
    let lonSum = 0;
    let count = 0;

    // Create markers for each station and add them to the map
    const showBoundaryStations = $('#show-boundary-stations-toggle').prop('checked');
    const filteredStations = showBoundaryStations ? stationData : stationData.filter(station => station.isin_boundary);

    // Clear all markers from the map
    clearMarkers(map);
    filteredStations.forEach(station => {
        const location = station.location;
        const lat = parseFloat(location.latitude);
        const lng = parseFloat(location.longitude);
        const marker = L.marker([lat, lng], {
            icon: station.isin_boundary ? GREEN_ICON : RED_ICON
        })
            .bindPopup(`<b>${station.name}</b>`)
            .addTo(map);

        latSum += lat;
        lonSum += lng;
        count++;
    });

    // Center the map on the mean latitude and longitude of all stations
    const meanLat = latSum / count;
    const meanLon = lonSum / count;
    map.setView([meanLat, meanLon], 12);
}

function getBoundaryId() {
    const urlParams = new URLSearchParams(window.location.search);
    const boundary_id = urlParams.get('boundary_id');
    return boundary_id;
}
function getCsrfToken() {
    return document.getElementsByName("csrfmiddlewaretoken")[0].value;
}

function clearMarkers(map) {
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });
}
