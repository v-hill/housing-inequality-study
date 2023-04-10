$(document).ready(function () {

    // Make an AJAX request to the Django view
    updateCards(createCards);

    $('#check_exists').click(function () {
        checkBoundaryExists();
    });

    $('#add_boundary').click(function () {
        $.ajax({
            url: 'map_boundaries/add_boundary/',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            data: {
                'osm_id': osmId
            },
            success: function (data) {
                // handle the response here
                updateCards(createCards);
                const responseText = document.getElementById('response-text');
                responseText.innerHTML = `Added boundary ${data.name}`;

                // hide the add button
                const buttonToHide = document.getElementById('add_boundary');
                buttonToHide.classList.add('hidden');
            },
            error: function (error) {
                console.error('Error adding new boundary:', error);

            }
        });
    });
});

function getCsrfToken() {
    return document.getElementsByName("csrfmiddlewaretoken")[0].value;
}

function createCards(data) {
    var cards = '';
    for (var i = 0; i < data.length; i++) {
        cards += `<div class='card'>
        <div class='card-body'>
            <h5 class='card-title'>${data[i].name}</h5>
            <p class='card-text'>Admin Level: ${data[i].admin_level}</p>
            <p class='card-text'>ISO 3166-2: ${data[i].iso31662}</p>
            <p class='card-text'>Ref GSS: ${data[i].ref_gss}</p>
            <button class="btn btn-primary boundary-button" data-boundary-id=${data[i].id}>View Details</button>
            <button class='delete-card btn btn-danger' data-id='${data[i].id}'>Delete</button>
        </div>
      </div>`;
    }

    // Update the card container
    $('#card-container').html(cards);

    // Attach click event listener to view details button
    addDetailPageListeners();

    // Attach click event listener to delete button
    addDeleteListners(createCards);
}



// Function to create cards from the data
function updateCards(createCards) {
    $.ajax({
        url: 'map_boundaries',
        type: 'GET',
        success: function (data) {
            // Assign the returned data to a variable
            var mapBoundaries = data;
            // Do something with the data, e.g. create cards
            createCards(mapBoundaries);
        },
        error: function (error) {
            console.error('Error updating cards:', error);
        }
    });
}

function addDetailPageListeners() {
    $('.boundary-button').on('click', function () {
        let boundary_id = $(this).data('boundary-id');
        // Redirect to the detailed page for the boundary, including the boundary_id as a query parameter
        window.location.href = `/publictransit/boundary?boundary_id=${boundary_id}`;
    });
}

function addDeleteListners(createCards) {
    $('.delete-card').click(function () {
        var cardId = $(this).data('id');
        console.log('deleting card with id:', cardId);

        // Make AJAX request to delete card
        $.ajax({
            url: 'map_boundaries/' + cardId + '/delete_boundary/',
            type: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            success: function (data) {
                // Update card list on success
                updateCards(createCards);
            },
            error: function (error) {
                console.error('Error deleting card:', error);
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
                // show the button
                const newButton = document.getElementById('add_boundary');
                newButton.classList.remove('hidden');
            }
        },
        error: function (error) {
            console.error('Error checking if boundary exists:', error);
            responseText.innerHTML = 'Error: Unable to fetch data';
        }
    });
}
