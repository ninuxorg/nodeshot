/*
 * this is just a temporary file for very basic features
 * will be converted to a more structured set of files with backbone.js
 */
// menu
$('#ns-top-nav-links > ul > li > a').click(function (e) {
    $('#ns-top-nav-links li.active').removeClass('active');
    $(this).parents('li').eq(0).addClass('active');
});

// set max height of collapsible menu (mobile)
var setCollapsibleMainMenuMaxHeight = function () {
    $('#nav-bar .navbar-collapse').css('max-height', $(window).height() - 50);
}

// dynamic map dimensions
var setMapDimensions = function () {
    if (!$('#map-overlay-container').length) {
        var height = $(window).height() - $('body > header').height();
        $('#map-container, #map-toolbar').height(height);
    } else {
        var height = $('#map-overlay-container').height() + parseInt($('#map-overlay-container').css('top'));
        $('#map-container').height(height);
    }

    var map_toolbar = $('#map-toolbar'),
        add_node_container = $('#add-node-container');
    width = $(window).width();

    // take in consideration #add-node-container if visible
    if (add_node_container.is(':visible')) {
        width = width - add_node_container.outerWidth();
    }
    // take in consideration map toolbar if visible
    else if (map_toolbar.is(':visible')) {
        width = width - map_toolbar.outerWidth();
    }
    $('#map').width(width);

    var map = Nodeshot.body.currentView.map;
    if (map && map.invalidateSize) {
        map.invalidateSize();
    }
}

// automatically center modal depending on its width
$('body').delegate('.modal.autocenter', 'show.bs.modal', function (e) {
    var dialog = $(this).find('.modal-dialog'),
        dialog_dimensions = dialog.getHiddenDimensions(),
        coefficient = $(this).attr('data-autocenter-coefficient');

    if (!coefficient) {
        coefficient = 2.1
    }

    dialog.css({
        width: dialog_dimensions.width,
        right: 0
    });

    // vertically align to center
    new_height = ($(window).height() - dialog_dimensions.height) / coefficient;
    // ensure new position is greater than zero
    new_height = new_height > 0 ? new_height : 0;
    // set new height
    dialog.css('top', new_height);
})

// get width of an hidden element
$.fn.getHiddenDimensions = function () {
    var self = $(this);

    // return immediately if element is visible
    if (self.is(':visible')) {
        return {
            width: self.outerWidth(),
            height: self.outerHeight()
        }
    }

    var hidden = self, // this element is hidden
        parents = self.parents(':hidden'); // look for hidden parent elements

    // if any hidden parent element
    if (parents.length) {
        // add to hidden collection
        hidden = $().add(parents).add(hidden);
    }

    /*
     trick all the hidden elements in a way that
     they wont be shown but we'll be able to calculate their width
    */
    hidden.css({
        position: 'absolute',
        visibility: 'hidden',
        display: 'block'
    });

    // store width of current element
    var dimensions = {
        width: self.outerWidth(),
        height: self.outerHeight()
    }

    // reset hacked css on hidden elements
    hidden.css({
        position: '',
        visibility: '',
        display: ''
    });

    // return width
    return dimensions;
}

clearPreloader = function () {
    $('#preloader').fadeOut(255, function () {
        // clear overflow hidden except if map view
        if (!$('#map').length) {
            $('body').removeAttr('style');
        }
    });
}

// map
$(window).resize(function (e) {
    setCollapsibleMainMenuMaxHeight();
}).load(function (e) {
    setCollapsibleMainMenuMaxHeight();
    clearPreloader();
});

$(document).ready(function ($) {
    $('#js-signup-password').pwstrength({
        common: {
            minChar: 1
        },
        ui: {
            container: "#js-password-strength-message",
            viewports: {
                progress: ".pwstrength_viewport_progress",
                verdict: ".pwstrength_viewport_verdict"
            },
            verdicts: ["Very weak", "Weak", "Normal", "Medium", "Strong"],
            scores: [10, 17, 26, 40, 50]
        }
        //bootstrap2: true
    }).focus(function (e) {
        $('#js-password-strength-message').fadeIn(255);
    });

    $('#mobile-nav').click(function (e) {
        e.preventDefault();
    });

    $('#nav-bar').delegate('#ns-top-nav-links.in a:not(.dropdown-toggle)', 'click', function (e) {
        $('#ns-top-nav-links').collapse('hide');
    });
});
