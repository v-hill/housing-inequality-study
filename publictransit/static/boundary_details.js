$(document).ready(function () {
    function updateStationsTable(data) {
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
    }

    $("#remove-stations-btn").on("click", function () {
        $.ajax({
            url: 'remove_stations',
            type: 'POST',
            success: function (data) {
                // Hide the remove-stations-btn and train-station-list
                $("#remove-stations-btn").hide();
                $("#train-station-list").hide();

                // Show the download-stations-btn
                $("#download-stations-btn").show();
            },
            error: function () {
                alert("An error occurred while removing the train stations data.");
            }
        });
    });

    $("#download-stations-btn").on("click", function () {
        $.ajax({
            url: 'download_stations_data',
            type: 'POST',
            success: function (data) {
                // Update the stations table, if needed
                updateStationsTable(data);

                // Show the remove-stations-btn and train-station-list
                $("#remove-stations-btn").show();
                $("#train-station-list").show();

                // Hide the download-stations-btn
                $("#download-stations-btn").hide();
            },
            error: function () {
                alert("An error occurred while downloading the train stations data.");
            }
        });
    });

    $.ajax({
        url: 'stations_data_exists',
        type: 'POST',
        success: function (data) {
            if (data.stations && data.stations.length > 0) {
                updateStationsTable(data);
                $("#download-stations-btn").hide();
                $("#remove-stations-btn").show();
            } else {
                $("#remove-stations-btn").hide();
                $("#download-stations-btn").show();
            }
        },
        error: function () {
            alert("An error occurred while fetching the train stations.");
        }
    });
});
