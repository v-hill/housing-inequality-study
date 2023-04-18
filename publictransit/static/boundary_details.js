$(document).ready(function () {
    // Get the boundary_id from the URL query parameter
    const boundary_id = getBoundaryId();
    getStationsFromDb(boundary_id);
    getPolygonCountFromDb(boundary_id);

    $("#remove-polygon-btn").on("click", function () {
        removePolygonData(boundary_id);
    });
    $("#download-polygon-btn").on("click", function () {
        downloadPolygonData(boundary_id);
    });
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
                $("#download-stations-btn").hide();
                $("#remove-stations-btn").show();
                $("#stations-map-btn").show();
            } else {
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

function getPolygonCountFromDb(boundary_id) {
    $.ajax({
        url: `polygon/count/?boundary_id=${boundary_id}`,
        type: 'GET',
        success: function (polygon) {
            if (polygon) {
                updatePolygonSummaryText(polygon);
                $("#download-polygon-btn").hide();
                $("#remove-polygon-btn").show();

            } else {
                $("#remove-polygon-btn").hide();
                $("#download-polygon-btn").show();
            }
        },
        error: function () {
            alert("An error occurred while fetching the train stations.");
        }
    });
}

function updatePolygonSummaryText(data) {
    console.log(data);
    var num_nodes = data.num_nodes ?? 0;
    $("#polygon-summary").text(`There are ${num_nodes} boundary nodes in the database for this boundary.`);
}

function updateStationSummaryText(stations) {
    var num_stations_within_boundary = stations?.filter(station => station.isin_boundary)?.length ?? 0;
    var num_stations_outside_boundary = stations?.filter(station => !station.isin_boundary)?.length ?? 0;
    $("#stations-summary").text(`There are ${num_stations_within_boundary} stations within the boundary and ${num_stations_outside_boundary} stations outside of the boundary.`);
}


function updateStationsTable(stations) {
    let stationList = '<table class="table table-sm">';
    stationList += "<tr><th>Name</th><th>Latitude</th><th>Longitude</th></tr>";
    stations.forEach(station => {
        stationList += "<tr";
        if (!station.isin_boundary) {
            stationList += ' class="table-danger"';
        } else {
            stationList += ' class="table-success"';
        }
        stationList += ">";
        stationList += `<td><a href="https://www.openstreetmap.org/node/${station.osm_id}" target="_blank">${station.name}</a></td>`;
        stationList += `<td>${station.location.latitude}</td>`;
        stationList += `<td>${station.location.longitude}</td>`;
        stationList += "</tr>";
    });

    stationList += "</table>";

    $("#train-station-list").html(stationList);
}


function removePolygonData(boundary_id) {
    $.ajax({
        url: `polygon/remove_data/?boundary_id=${boundary_id}`,
        type: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        success: function (data) {
            updatePolygonSummaryText(data);
            $("#remove-polygon-btn").hide(); // Hide elements
            $("#download-polygon-btn").show(); // Show elements
        },
        error: function () {
            alert("An error occurred while removing the boundary polygon data.");
        }
    });
}

function downloadPolygonData(boundary_id) {
    $.ajax({
        url: `polygon/download_data/?boundary_id=${boundary_id}`,
        type: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        success: function (data) {
            updatePolygonSummaryText(data);
            $("#download-polygon-btn").hide(); // Hide elements
            $("#remove-polygon-btn").show(); // Show elements
        },
        error: function () {
            alert("An error occurred while downloading the boundary polygon data.");
        }
    });
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
