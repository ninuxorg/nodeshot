/*
 * this is just a temporary file for very basic features
 * will be converted to a more structured set of files with backbone.js
*/

// menu
$('#ns-top-nav-links > ul > li > a').click(function(e){
	$('#ns-top-nav-links li.active').removeClass('active');
	$(this).parents('li').eq(0).addClass('active');
});

// set max height of collapsible menu (mobile)
var setCollapsibleMainMenuMaxHeight = function(){
	$('#nav-bar .navbar-collapse').css('max-height', $(window).height()-50);
}

// dynamic map dimensions
var setMapDimensions = function(){
	var height = $(window).height() - $('body > header').height();
	$('#map-container, #map-toolbar').height(height);
	
    var map_toolbar = $('#map-toolbar'),
        width = $(window).width();
    
    // take in consideration map toolbar if visible
    if(map_toolbar.is(':visible')){
        width = width - $('#map-toolbar').width();
    }
	$('#map').width(width);
}

var setNotificationsLeft = function(){
	var left = $('#top-bar .notifications').offset().left,
		button_width = $('#top-bar .notifications').outerWidth();
		notifications_width = $('#notifications').getHiddenDimensions().width;
	
	$('#notifications').css('left', left - notifications_width/2 + button_width/2);
}

var toggleLoading = function(){
	$('#loading').fadeToggle(255);
}

// close loading
$('#loading .icon-close').click(function(e){
	toggleLoading();
});

// automatically center modal depending on its width
$('.modal.autocenter').on('show.bs.modal', function(e) {
    var dialog = $(this).find('.modal-dialog'),
        dialog_dimensions = dialog.getHiddenDimensions(),
        coefficient = $(this).attr('data-autocenter-coefficient');
    
    if(!coefficient){
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
$.fn.getHiddenDimensions = function(){
    var self = $(this);
    
	// return immediately if element is visible
	if(self.is(':visible')){
        return {
			width: self.outerWidth(),
			height: self.outerHeight()
		}
    }
    
    var hidden = self,  // this element is hidden
        parents = self.parents(':hidden');  // look for hidden parent elements
        
    // if any hidden parent element
    if(parents.length){
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

clearPreloader = function(){
    $('#preloader').fadeOut(255, function(){
		// clear overflow hidden except if map view
		if(!$('#map').length) {
			$('body').removeAttr('style');
		}
    });
}

// search (ugly global var!)
var searchLoadingIndicator = $('#general-search .animate-spin'),
    searchIcon = $('#general-search .icon-search'),
    searchResults = $('#general-search ul'),
    showSearchSpinner = function(){
        searchIcon.hide();
        searchLoadingIndicator.fadeIn(255);
        searchResults.fadeIn(255);
    },
    hideSearchSpinner = function(){
        searchLoadingIndicator.hide();
        searchIcon.fadeIn(255);
        searchResults.fadeOut(255);
    };

$('#general-search-input').keyup(function(e){
    if(this.value.length > 2 && searchLoadingIndicator.is(':hidden')){
        showSearchSpinner();
    }
    else if(this.value.length < 3 && searchLoadingIndicator.is(':visible')){
        hideSearchSpinner();
    }
}).blur(function(e){
    hideSearchSpinner();
});

// map
$(window).resize(function(e){
	setCollapsibleMainMenuMaxHeight();
	setMapDimensions();
	setNotificationsLeft();
}).load(function(e){
	setCollapsibleMainMenuMaxHeight();
    clearPreloader();
});

$(document).ready(function($){   
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
    }).focus(function(e){
        $('#js-password-strength-message').fadeIn(255);
    });
    
    $('#mobile-nav').click(function(e){
        e.preventDefault();
    });
    
    $('#nav-bar').delegate('#ns-top-nav-links.in a:not(.dropdown-toggle)', 'click', function(e){
        $('#ns-top-nav-links').collapse('hide');
    });
});

$('#main-actions .notifications').click(function(e){
	e.preventDefault();
	
	var notifications = $('#notifications');
	
	if (notifications.is(':hidden')) {
		setNotificationsLeft();
		
		notifications.fadeIn(255, function(){
			$('#notifications .scroller').scroller('reset');
			
			$('html').one('click',function() {
				notifications.fadeOut(150);
			});
		});
	}
	else{
		notifications.fadeOut(150);
	}
});

$('#notifications').click(function(e){
	e.stopPropagation();
});

$('#notifications .scroller').mouseenter(function(e){
	$('.scroller-bar').fadeIn(255);
}).mouseleave(function(e){
	$('.scroller-bar').fadeOut(255);
});

/* --- settings --- */

// implement String trim for older browsers
if (!String.prototype.trim) {
    String.prototype.trim = $.trim;
}

// extend jquery to be able to retrieve a cookie
$.getCookie = function(name) {
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

$.csrfSafeMethod = function(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.sameOrigin = function(url) {
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
    beforeSend: function(xhr, settings) {
        if (!$.csrfSafeMethod(settings.type) && $.sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", $.getCookie('csrftoken') || window.sharigo.initial_csfr_token);
        }
    }
});