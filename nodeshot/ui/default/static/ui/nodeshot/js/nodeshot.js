/*
 * this is just a temporary file for very basic features
 * will be converted to a more structured set of files with backbone.js
*/

$('#ns-top-nav-links > ul > li > a').click(function(e){
	e.preventDefault();
	$('#ns-top-nav-links li.active').removeClass('active');
	$(this).parents('li').eq(0).addClass('active');
});

// truncate long usernames
var $username = $('#username-js');
if($username.text().length > 15){
	var truncated = $username.text().substr(0, 13) + "&hellip;";
	$username.html(truncated);
}

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
	//var 
	var left = $('#top-bar .notifications').offset().left,
		button_width = $('#top-bar .notifications').outerWidth();
		notifications_width = $('#notifications').getHiddenDimensions().width;
	//left
	$('#notifications').css('left', left - notifications_width/2 + button_width/2);
}

var toggleLoading = function(){
	$('#loading').fadeToggle(255);
}

// close loading
$('#loading .icon-close').click(function(e){
	toggleLoading();
});

// init tooltip
$('#map-toolbar a, .hastip').tooltip();

// map toolbar buttons
$('#map-toolbar a').click(function(e){
	e.preventDefault();
	
	var button = $(this),
		panel_id = button.attr('data-panel'),
		panel = $('#' + panel_id),
		other_panels = $('.side-panel:not(#'+panel_id+')');
	
	// if no panel return here
	if (!panel.length) {
		return;
	}
	
	// hide all other open panels
	other_panels.hide();
	// hide any open tooltip
	$('#map-toolbar .tooltip').hide();
	$('#map-toolbar a').removeClass('active');
	
	if (panel.is(':hidden')) {
		var distance_from_top = button.offset().top - $('body > header').eq(0).outerHeight();
		panel.css('top', distance_from_top);
		
		
		// here we should use an event
		if (panel.hasClass('adjust-height')) {
			var preferences_height = $('#map-container').height() - distance_from_top -18;
			panel.height(preferences_height);
		}
		
		panel.show();
		$('.scroller').scroller('reset');
		button.addClass('active');
		button.tooltip('disable');
	}
	else{
		panel.hide();
		button.tooltip('enable');
	}
});

// correction for map tools
$('#map-toolbar a.icon-tools').click(function(e){
	var button = $(this),
		preferences_button = $('#map-toolbar a.icon-config');
	if(button.hasClass('active')) {
		preferences_button.tooltip('disable');
	}
	else{
		preferences_button.tooltip('enable');
	}
});

// correction for map-filter
$('#map-toolbar a.icon-layer-2').click(function(e){
	var button = $(this),
		other_buttons = $('a.icon-config, a.icon-3d, a.icon-tools', '#map-toolbar');
	if(button.hasClass('active')) {
		other_buttons.tooltip('disable');
	}
	else{
		other_buttons.tooltip('enable');
	}
});

// disable map stuff
$('#map-legend a:not(.icon-close)').click(function(e){
	e.preventDefault();
	
	var li = $(this).parent();
	
	if (li.hasClass('disabled')) {
		li.removeClass('disabled');
	}
	else{
		li.addClass('disabled');
	}
	
});

$('#btn-legend, #map-legend .icon-close').click(function(e){
	var legend = $('#map-legend'),
		button = $('#btn-legend');
	
	if(legend.is(':visible')){
		legend.fadeOut(255);
		button.removeClass('disabled');
		button.tooltip('enable');
	}
	else{
		legend.fadeIn(255);
		button.addClass('disabled');
		button.tooltip('disable').tooltip('hide');
	}
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

// add node
$('#map-toolbar .icon-pin-add').click(function(e){
    $('#map-legend .icon-close').trigger('click');
    
    var dialog = $('#step1'),
        dialog_dimensions = dialog.getHiddenDimensions();
    
    dialog.css({
        width: dialog_dimensions.width,
        right: 0
    });
    
    // vertically align to center
    //dialog.css('top', $(window).height()/2.1 - dialog_dimensions.height);
    dialog.fadeIn(255);
    
    $('#step1 button').click(function(e){
        $('#step1').hide();
        var dialog = $('#step2'),
        dialog_dimensions = dialog.getHiddenDimensions();
    
        dialog.css({
            width: dialog_dimensions.width,
            right: 0
        });
        
        // vertically align to center
        //dialog.css('top', $(window).height()/2.1 - dialog_dimensions.height);
        dialog.fadeIn(255);
    });
});

$('#fn-map-tools .tool').click(function(e){
	e.preventDefault();
	var button = $(this),
		active_buttons = $('#fn-map-tools .tool.active');
	
	if(!button.hasClass('active')){
		// deactivate any other
		active_buttons.removeClass('active');
		active_buttons.tooltip('enable');
		
		button.addClass('active');
		button.tooltip('hide');
		button.tooltip('disable');
	}
	else{
		button.removeClass('active');
		button.tooltip('enable');
	}
});

// show map toolbar on mobile
$('#toggle-toolbar').click(function(e){
    e.preventDefault();
    $('#map-toolbar').toggle();
    setMapDimensions();
});

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
	setMapDimensions();
    clearPreloader();
});

$(document).ready(function($){
    // The axis option is for setting the dimension in
    // which the scrollbar should operate.
	$(".scroller").scroller({
		trackMargin: 6
	});
    
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
    
    // activate switch
    $('input.switch').bootstrapSwitch();
	$('input.switch').bootstrapSwitch('setSizeClass', 'switch-small');
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