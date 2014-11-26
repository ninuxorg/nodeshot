/*
 * this is just a temporary file for very basic features
 * will be converted to a more structured set of files with backbone.js
 */

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

clearPreloader = function () {
    $('#preloader').fadeOut(255, function () {
        // clear overflow hidden except if map view
        if (!$('#map').length) {
            $('body').removeAttr('style');
        }
    });
}

$(window).load(function(e){
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

    // menu
    $('#nav-bar').delegate('#ns-top-nav-links li a', 'click', function (e) {
        var a = $(this);
        if (a.attr('href').substr(0, 10) != 'javascript') {
            if(!a.hasClass('dropdown-toggle')){
                $('#ns-top-nav-links li.active').removeClass('active');
            }
        }
    });
});
