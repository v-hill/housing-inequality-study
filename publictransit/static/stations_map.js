$(document).ready(function () {
    // Create the map
    const map = L.map('map');
    const boundary_id = getBoundaryId();

    // Add a tile layer to the map
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Fetch train station data from the Django view
    $.ajax({
        url: `stations?boundary_id=${boundary_id}`,
        type: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        success: function (stations) {
            let latSum = 0;
            let lonSum = 0;
            let count = 0;

            // Create markers for each station and add them to the map
            stations.forEach(station => {
                const location = station.location;
                const lat = parseFloat(location.latitude);
                const lng = parseFloat(location.longitude);
                const marker = L.marker([lat, lng])
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
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error("Ajax request failed to fetch train stations map data: " + textStatus + ", " + errorThrown);
            console.log("Response status: " + jqXHR.status);
        }
    });
});

function getBoundaryId() {
    const urlParams = new URLSearchParams(window.location.search);
    const boundary_id = urlParams.get('boundary_id');
    return boundary_id;
}
function getCsrfToken() {
    return document.getElementsByName("csrfmiddlewaretoken")[0].value;
}
