$(document).ready(function () {
    // Create the map
    const map = L.map('map');

    // Add a tile layer to the map
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Fetch train station data from the Django view
    $.ajax({
        url: 'stations_in_db',
        type: 'GET',
        success: function (data) {
            let latSum = 0;
            let lonSum = 0;
            let count = 0;
            var stations = data.stations;

            // Create markers for each station and add them to the map
            stations.forEach(station => {
                const location = station.location;
                const marker = L.marker([location.latitude, location.longitude])
                    .bindPopup(`<b>${station.name}</b><br>OSM ID: ${station.osm_id}`)
                    .addTo(map);

                latSum += location.latitude;
                lonSum += location.longitude;
                count++;
            });

            // Center the map on the mean latitude and longitude of all stations
            const meanLat = latSum / count;
            const meanLon = lonSum / count;
            map.setView([meanLat, meanLon], 13);
        },
        error: function (err) {
            console.error("Error fetching stations data:", err);
        }
    });
});
