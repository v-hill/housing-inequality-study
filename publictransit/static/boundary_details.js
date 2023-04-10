$(document).ready(function () {
    // Get the boundary_id from the URL query parameter
    const boundary_id = getBoundaryId();
    getStationsFromDb(boundary_id);

    $("#remove-stations-btn").on("click", function () {
        removeStationsData(boundary_id);
    });

    $("#download-stations-btn").on("click", function () {
        downloadStationsData(boundary_id);
    });
});

function getCsrfToken() {
    return document.getElementsByName("csrfmiddlewaretoken")[0].value;
}

function getBoundaryId() {
    const urlParams = new URLSearchParams(window.location.search);
    const boundary_id = urlParams.get('boundary_id');
    return boundary_id;
}

function getStationsFromDb(boundary_id) {
    $.ajax({
        url: `stations?boundary_id=${boundary_id}`,
        type: 'GET',
        success: function (stations) {
            if (stations && stations.length > 0) {
                updateStationSummaryText(stations);
                updateStationsTable(stations);
                // Update visible elements
                $("#download-stations-btn").hide();
                $("#remove-stations-btn").show();
                $("#stations-map-btn").show();
            } else {
                // Update visible elements
                $("#remove-stations-btn").hide();
                $("#stations-map-btn").hide();
                $("#download-stations-btn").show();
            }
        },
        error: function () {
            alert("An error occurred while fetching the train stations.");
        }
    });
}

function updateStationSummaryText(stations) {
    var num_stations = stations?.length ?? 0;
    $("#stations-summary").text("There are " + num_stations + " stations in the database for this area.");
}

function updateStationsTable(stations) {
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


function removeStationsData(boundary_id) {
    $.ajax({
        url: `stations/remove_data/?boundary_id=${boundary_id}`,
        type: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        success: function (data) {
            updateStationSummaryText(data.stations);
            updateStationsTable(data.stations);
            // Hide elements
            $("#remove-stations-btn").hide();
            $("#stations-map-btn").hide();
            $("#train-station-list").hide();
            // Show elements
            $("#download-stations-btn").show();
        },
        error: function () {
            alert("An error occurred while removing the train stations data.");
        }
    });
}

function downloadStationsData(boundary_id) {
    $.ajax({
        url: `stations/download_data/?boundary_id=${boundary_id}`,
        type: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        success: function (data) {
            updateStationSummaryText(data.stations);
            updateStationsTable(data.stations);
            // Show elements
            $("#remove-stations-btn").show();
            $("#stations-map-btn").show();
            $("#train-station-list").show();
            // Hide elements
            $("#download-stations-btn").hide();
        },
        error: function () {
            alert("An error occurred while downloading the train stations data.");
        }
    });
}
