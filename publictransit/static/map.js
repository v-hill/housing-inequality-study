$(document).ready(function () {
    const defaultLat = 51.50129;
    const defaultLon = -0.14182;

    // Initialize the map
    var mymap = L.map('map').setView([defaultLat, defaultLon], 14);

    // Add the OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 18,
    }).addTo(mymap);

    // Create a marker and add it to the map
    var markerLatlng = L.latLng(defaultLat, defaultLon);
    var marker = L.marker(markerLatlng).addTo(mymap);

    // get a reference to the search button
    var searchButton = $('#search-button');

    // add a click event listener to the search button
    searchButton.click(function () {
        // get the latitude and longitude values from the input fields
        var lat = document.getElementById("lat-input").value;
        var lng = document.getElementById("lng-input").value;

        // make an AJAX request to the search endpoint
        $.ajax({
            url: 'search',
            type: 'GET',
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
                mymap.setView(markerLatlng, 14);
            },
            error: function (xhr, status, error) {
                // Display an error message in the HTML page
                $('#error-message').text('Error: ' + xhr.responseText);
            }
        });
    });
});


window.onload = function () {
    // Clear value of latitude on page load
    document.getElementById("lat-input").value = "";
    document.getElementById("lng-input").value = "";

    function removeNonNumericChars(inputIds) {
        /**
         * Removes non-numeric characters from the input values of multiple HTML input elements.
         *
         * @param {string[]} inputIds - An array of input element ids to apply the function to.
         */
        inputIds.forEach(function (id) {
            var inputElement = document.getElementById(id);

            // Remove non-numeric characters on input
            inputElement.addEventListener("input", function () {
                this.value = this.value.replace(/[^0-9.-]/g, '');
            });
        });
    }
    removeNonNumericChars(["lat-input", "lng-input"]);
};
