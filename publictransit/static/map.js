$(document).ready(function () {
    // Initialize the map
    var mymap = L.map('map').setView([51.505, -0.09], 13);

    // Add the OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 18,
    }).addTo(mymap);

    // get a reference to the search button
    var searchButton = $('#search-button');

    // add a click event listener to the search button
    searchButton.click(function () {
        // get the latitude and longitude values from the input fields
        var lat = document.getElementById("lat-input").value;
        var lng = document.getElementById("lng-input").value;

        // make an AJAX request to the search endpoint
        $.ajax({
            type: 'GET',
            url: 'search',
            data: { 'lat': lat, 'lng': lng },
            beforeSend: function () {
                // Clear any existing error message
                $('#error-message').empty();
            },
            success: function (data) {
                // Remove all existing markers
                mymap.eachLayer(function (layer) {
                    if (layer instanceof L.Marker) {
                        mymap.removeLayer(layer);
                    }
                });

                // Create a marker and add it to the map
                var markerLatlng = L.latLng(data.lat, data.lng);
                var marker = L.marker(markerLatlng).addTo(mymap);

                // Center map on the new marker location
                mymap.setView(markerLatlng, 12);
            },
            error: function (xhr, status, error) {
                // Display an error message in the HTML page
                $('#error-message').text('Error: ' + xhr.responseText);
            }
        });
    });
});
