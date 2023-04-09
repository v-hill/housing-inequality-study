$(document).ready(function () {
    $("#get-all-stations-btn").on("click", function () {
        $.ajax({
            url: 'train_stations',
            type: 'POST',
            success: function (data) {
                var stations = data.stations;
                let stationList = '<table class="table table-sm">';
                stationList += "<tr><th>Name</th><th>Latitude</th><th>Longitude</th></tr>";
                stations.forEach(station => {
                    stationList += "<tr>";
                    stationList += `<td><a href="https://www.openstreetmap.org/node/${station.osm_id}" target="_blank">${station.name}</a></td>`;
                    stationList += `<td>${station.location.latitude}</td>`;
                    stationList += `<td>${station.location.longitude}</td>`;
                    stationList += "</tr>";
                });

                stationList += "</table>";

                $("#train-station-list").html(stationList);
            },
            error: function () {
                alert("An error occurred while fetching the train stations.");
            }
        });
    });
});
