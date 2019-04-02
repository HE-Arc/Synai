/**
 * Feed JS
 * 
 * This files contains all the java script code of the template feed.html
 */

 //
 // AJAX functions
//


/**
 * Search a value (song, artist, album) and
 * display the result on the page
 */
$("#search_button").click(function(){
    let search_field_input = $("#search_field").val();
    if (search_field_input){
        $.ajax({
            url: "/search_results",
            type: 'GET',
            data: {
                'search_input': search_field_input
            },
            dataType: 'html',
            success: function(data) {
                $("#search-content").html(data);
            }
        });
    }
});

/**
 * Activate the click event on the search button
 * when enter is pressed when the searched field
 * has focus
 */
$('#search_field').keypress(function (e) {
    if (e.which === 13)
    {
        e.preventDefault();
        $('#search_button').click();
    }
});

/**
 * Load the user playlist when the pill tab of playlist
 * is clicked
 */
$('#pills-playlist-tab').click(function(){
    $('#pills-playlist').load("/playlist_entries");
});

/**
 * Request a playlist analysis using its id
 * @param {*} playlist_id spotify id of the playlist
 * @param {*} playlist_name playlist name
 */
function analysePlaylist(playlist_id, playlist_name) {
    $("#analyse_results").html('<div class="d-flex justify-content-center"><div class="spinner-border" style="width: 3rem; height: 3rem;" role="status"><span class="sr-only">Loading...</span></div></div>');
    $.ajax({
        url: "/analyse",
        type: 'GET',
        data: {
            'id': playlist_id,
            'name': playlist_name,
            'type' : 'playlist',
        },
        dataType: 'html',
        success: function(data) {
            $("#analyse_results").html(data);
        }
    });
}

/**
 * Analyse the history of the current user when a 
 * card of playlist is pressed
 */
function analyseHistory() {
    $("#analyse_results").html('<div class="d-flex justify-content-center"><div class="spinner-border" style="width: 3rem; height: 3rem;" role="status"><span class="sr-only">Loading...</span></div></div>');
    $.ajax({
        url: "/analyse",
        type: 'GET',
        data: {
            'type' : 'history',
        },
        dataType: 'html',
        success: function(data) {
            $("#analyse_results").html(data);
        }
    });
}