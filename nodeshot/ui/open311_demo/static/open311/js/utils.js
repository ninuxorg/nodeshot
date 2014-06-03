/* UTILITIES
 * ==========*/

function latLngtoWKT(lng, lat) {
    return "POINT(" + lng + " " + lat + ")";
}

function escapeHtml(unsafe) {
    return unsafe.replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getData(url) {
    /*
     * Get Data in async way, so that it can return an object to a variable
     */
    var data;
    $.ajax({
        async: false, //thats the trick
        url: url,
        dataType: 'json',
        success: function (response) {
            data = response;
        }

    });
    return data;
}


function getAddress(lat,lng) {
    /*
     * Get Address using OSM Nominatim service
     */
    var url = 'https://nominatim.openstreetmap.org/reverse?format=json&lat=' + lat + '&lon=' + lng + '&zoom=18&addressdetails=1';
    $.ajax({
        async: true,
        url: url,
        dataType: 'json',
        success: function (response) {
            data = {}
            data = response;
            address = data.display_name;
            $("#requestAddress").val(address);
            $("#loadingAddress").hide();
        }

    });
}



$(document).ajaxStart(function () {
    $('#loading').show();
});
$(document).ajaxStop(function () {
    $('#loading').hide();
});

function convertToSlug(Text) {
    return Text.toLowerCase()
        .replace(/[^\w ]+/g, '')
        .replace(/ +/g, '-');
}

//function geojsonColl() {
//    this.type="FeatureCollection",
//    this.features= [] };
//    
//function featureConstructor() {
//    this.type="Feature",
//    this.geometry = {"type":"Point",}
//    this.properties = {}
//    };
    
    /* AUTHENTICATION
 * ============== */

$.getCookie = function (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');

        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.sameOrigin = function (url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
    // or any other URL that isn't scheme relative or absolute i.e relative.
    !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!$.csrfSafeMethod(settings.type) && $.sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", $.getCookie('csrftoken'));
        }
    },
    error: function (jqXHR, exception) {
            if (jqXHR.status === 0) {
                alert('Not connect.\n Verify Network.');
            } else if (jqXHR.status == 404) {
                alert('Requested page not found. [404]');
            } else if (jqXHR.status == 500) {
                alert('Internal Server Error [500].');
            } else if (exception === 'parsererror') {
                alert('Requested JSON parse failed.');
            } else if (exception === 'timeout') {
                alert('Time out error.');
            } else if (exception === 'abort') {
                alert('Ajax request aborted.');
            } else {
                alert('Uncaught Error.\n' + jqXHR.responseText);
            }
        }
    
});

