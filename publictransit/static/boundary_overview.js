$(document).ready(function () {
    // Make an AJAX request to the Django view
    updateCards(createCards);

    $('#check_exists').click(function () {
        checkBoundaryExists();
    });

    $('#add_boundary').click(function () {
        $.ajax({
            url: 'add_boundary',
            type: 'POST',
            data: {
                'osm_id': osmId
            },
            success: function (data) {
                // handle the response here
                updateCards(createCards);
                responseText.innerHTML = `Added boundary ${data.name}`;

                // hide the add button
                const buttonToHide = document.getElementById('add_boundary');
                buttonToHide.classList.add('hidden');
            },
            error: function (xhr, status, error) {
                console.log("error!")

            }
        });
    });
});



function createCards(data) {
    var cards = '';
    for (var i = 0; i < data.length; i++) {
        cards += `<div class='card'>
        <div class='card-body'>
            <h5 class='card-title'>${data[i].name}</h5>
            <p class='card-text'>Admin Level: ${data[i].admin_level}</p>
            <p class='card-text'>ISO 3166-2: ${data[i].iso31662}</p>
            <p class='card-text'>Ref GSS: ${data[i].ref_gss}</p>
            <a href='/publictransit/boundary/${data[i].id}/' class='btn btn-primary'>View Details</a>
            <button class='delete-card btn btn-danger' data-id='${data[i].id}'>Delete</button>
        </div>
      </div>`;
    }

    // Update the card container
    $('#card-container').html(cards);

    // Attach click event listener to delete button
    addDeleteListners(createCards);
}

// Function to create cards from the data
function updateCards(createCards) {
    $.ajax({
        url: 'list_boundaries',
        type: 'GET',
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
    $('.delete-card').click(function () {
        var cardId = $(this).data('id');
        console.log('deleting card with id:', cardId);

        // Include CSRF token in request headers
        var csrftoken = $('[name=csrfmiddlewaretoken]').val();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        });

        // Make AJAX request to delete card
        $.ajax({
            url: 'delete_boundary',
            type: 'DELETE',
            data: { 'boundary_id': cardId },
            success: function (data) {
                // Update card list on success
                updateCards(createCards);
            },
            error: function (xhr, status, error) {
                console.log('Error deleting card:', error);
            }
        });
    });
}

function updatePlaceholder() {
    const areaStandardSelect = document.getElementById('area-standard');
    const areaValueInput = document.getElementById('area-value');

    if (areaStandardSelect.value === 'Ref GSS') {
        areaValueInput.placeholder = 'E09000001';
    } else if (areaStandardSelect.value === 'ISO 3166-2') {
        areaValueInput.placeholder = 'GB-LND';
    }
}

function checkBoundaryExists() {
    const areaStandardSelect = document.getElementById('area-standard');
    const areaValueInput = document.getElementById('area-value');
    const responseText = document.getElementById('response-text');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            responseText.innerHTML = 'Checking...';
        }
    });
    $.ajax({
        url: 'check_boundary',
        type: 'GET',
        data: {
            area_standard: areaStandardSelect.value,
            area_value: areaValueInput.value
        },
        dataType: 'json',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        success: function (data) {
            if (data.error) {
                responseText.innerHTML = `Error: ${data.error}`;
            } else {
                responseText.innerHTML = data.success;
                osmId = data.osm_id;
                console.log(osmId);
                // show the button
                const newButton = document.getElementById('add_boundary');
                newButton.classList.remove('hidden');
            }
        },
        error: function (error) {
            console.error('Error:', error);
            responseText.innerHTML = 'Error: Unable to fetch data';
        }
    });
}
