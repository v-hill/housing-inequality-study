$(document).ready(function () {
    // Make an AJAX request to the Django view
    updateCards(createCards);

});

function createCards(data) {
    var cards = "";
    for (var i = 0; i < data.length; i++) {
        cards += "<div class='card'><div class='card-body'><h5 class='card-title'>"
            + data[i].name + "</h5><p class='card-text'>Admin Level: "
            + data[i].admin_level + "</p><p class='card-text'>ISO 3166-2: "
            + data[i].iso31662
            + "</p><p class='card-text'>Openstreetmap ID: "
            + data[i].osm_id
            + "</p><p class='card-text'>Ref GSS: "
            + data[i].ref_gss + "</p></div></div>"
            + "<button class='delete-card btn btn-danger' data-id='"
            + data[i].id
            + "'>Delete</button>";
    }

    // Update the card container
    $("#card-container").html(cards);

    // Attach click event listener to delete button
    addDeleteListners(createCards);
}

// Function to create cards from the data
function updateCards(createCards) {
    $.ajax({
        type: 'GET',
        url: 'boundaries',
        success: function (data) {
            // Assign the returned data to a variable
            var mapBoundaries = data;
            // Do something with the data, e.g. create cards
            createCards(mapBoundaries);
        },
        error: function (xhr, status, error) {
            // Display an error message in the HTML page
            $('#error-message').text('Error: ' + xhr.responseText);
        }
    });
}

function addDeleteListners(createCards) {
    $(".delete-card").click(function () {
        var cardId = $(this).data("id");
        console.log('deleting card with id:', cardId);

        // Include CSRF token in request headers
        var csrftoken = $("[name=csrfmiddlewaretoken]").val();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        });

        // Make AJAX request to delete card
        $.ajax({
            url: "delete_card",
            type: "DELETE",
            data: { 'boundary_id': cardId },
            success: function (result) {
                // Update card list on success
                updateCards(createCards);
            },
            error: function (xhr, status, error) {
                console.log("Error deleting card:", error);
            }
        });
    });
}
