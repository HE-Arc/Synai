/**
 * Feed JS
 * 
 * This files contains all the java script code of the template feed.html
 */

/**
 * Display a load spinner
 */
function analysisWait() {
    $("#analyse_results").html('<div class="d-flex justify-content-center"><div class="spinner-border" style="width: 3rem; height: 3rem;" role="status"><span class="sr-only">Loading...</span></div></div>');
}

/**
 * Display an alert message and stop the loading spinner
 */
function analysisFail(){
    alert("Oups ! Something went wrong... We cannot analyse your songs.");
    $("#analyse_results").html("");
}

/**
 * Load the user playlist when the pill tab of playlist
 * is clicked
 */
$('#pills-playlist-tab').click(function(){
    $('#pills-playlist').load("/playlist_entries");
});

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
 * Request a playlist analysis using its id
 * @param {*} playlist_id spotify id of the playlist
 * @param {*} playlist_name playlist name
 */
function analysePlaylist(playlist_id, playlist_name) {
    analysisWait();
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
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            analysisFail();
        },
    });
}

/**
 * Analyse the history of the current user when a 
 * card of playlist is pressed
 */
function analyseHistory() {
    analysisWait();
    $.ajax({
        url: "/analyse",
        type: 'GET',
        data: {
            'type' : 'history',
        },
        dataType: 'html',
        success: function(data) {
            $("#analyse_results").html(data);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            analysisFail();
        },
    });
}

/**
 * Request an artist analysis using its id
 * @param {*} artist_id 
 * @param {*} src_name 
 */
function analyseArtist(artist_id, src_name) {
    analysisWait();
    $.ajax({
        url: "/analyse",
        type: 'GET',
        data: {
            'id': artist_id,
            'name': src_name,
            'type' : 'artist',
        },
        dataType: 'html',
        success: function(data) {
            $("#analyse_results").html(data);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            analysisFail();
        },
    });
}

/**
 * Request a single song analysis using its id
 * @param {*} song_id 
 * @param {*} src_name 
 */
function analyseSong(song_id, src_name) {
    analysisWait();
    $.ajax({
        url: "/analyse",
        type: 'GET',
        data: {
            'id': song_id,
            'name': src_name,
            'type' : 'song',
        },
        dataType: 'html',
        success: function(data) {
            $("#analyse_results").html(data);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            analysisFail();
        },
    });
}

/**
 * Request an album analysis using its id
 * @param {*} album_id 
 * @param {*} src_name 
 */
function analyseAlbum(album_id, src_name) {
    analysisWait();
    $.ajax({
        url: "/analyse",
        type: 'GET',
        data: {
            'id': album_id,
            'name': src_name,
            'type' : 'album',
        },
        dataType: 'html',
        success: function(data) {
            $("#analyse_results").html(data);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            analysisFail();
        },
    });
}