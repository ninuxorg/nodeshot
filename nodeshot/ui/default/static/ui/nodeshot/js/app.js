var Page = Backbone.Model.extend({
    urlRoot : '/api/v1/pages/',
    idAttribute: 'slug',
    
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var AccountMenuView = Backbone.Marionette.ItemView.extend({
    el: '#main-actions',
    //className: 'center-stage multicolumn-md',
    template: '#account-menu-template',
	
	events: {
		'click #js-logout': 'logout',
		'click .notifications': 'openNotificationsPanel'
	},
	
	initialize: function(){
		this.truncateUsername();
		
		var self = this;
		
		// listen to models change and update accordingly
		// used for login/logout rendering
		this.listenTo(this.model, "change", function(){
			self.render();
		});
	},
	
	/*
	 * truncate long usernames
	 */
	truncateUsername: function(){
		var username = this.model.get('username');
		
		if (typeof(username) !== 'undefined' && username.length > 15) {
			// add an ellipsis if username is too long
			var truncated = username.substr(0, 13) + "&hellip;";
			// update model
			this.model.set('username', truncated);
		}
	},
	
	/*
	 * logout
	 */
	logout: function(e){
		e.preventDefault();
		Nodeshot.currentUser.set('username', undefined);
		$.post('api/v1/account/logout/').error(function(){
			// TODO: improve!
			createModal({ message: 'problem while logging out' });
		});
	},
	
	/*
	 * open notifications panel
	 */
	openNotificationsPanel: function(e){
		e.preventDefault();
	
		var notifications = $('#notifications');
		
		// show panel if hidden
		if (notifications.is(':hidden')) {
			setNotificationsLeft();
			
			notifications.fadeIn(255, function(){
				// prepare scroller
				$('#notifications .scroller').scroller('reset');
				
				// clicking anywhere else closes the panel
				$('html').one('click',function() {
					notifications.fadeOut(150);
				});
			});
		}
		else{
			notifications.fadeOut(150);
		}
	}
});

var PageView = Backbone.Marionette.ItemView.extend({
    tagName: 'article',
    className: 'center-stage multicolumn-md',
    template: '#page-template'
});

var MapView = Backbone.Marionette.ItemView.extend({
    id: 'map-container',
    template: '#map-template',
    
    ui: {
		'toolbar': '#map-toolbar',
        'toolbarButtons': '#map-toolbar a',
        'legendTogglers': '#btn-legend, #map-legend a.icon-close',
        'switchMapMode': '#btn-map-mode',
		'legend': '#map-legend',
		'legendButton': '#btn-legend',
		'addNodeStep1': '#add-node-step1',
		'addNodeStep2': '#add-node-step2',
		'addNodeContainer': '#add-node-container',
		'addNodeForm': '#add-node-form'
    },
    
    events: {
        'click #map-toolbar .icon-pin-add': 'addNode',
        'click @ui.toolbarButtons': 'togglePanel',
        'click @ui.legendTogglers': 'toggleLegend',
        'click #map-legend li a': 'toggleLegendControl',
        'click #fn-map-tools .tool': 'toggleTool',
        'click #toggle-toolbar': 'toggleToolbar',
        'click @ui.switchMapMode': 'switchMapMode',
		'click #add-node-form .btn-default': 'closeAddNode',
        'submit #add-node-form': 'submitAddNode'
    },
	
	initialize: function(){
		// bind to namespaced events
        $(window).on("beforeunload.map", _.bind(this.beforeunload, this));
		$(window).on("resize.map", _.bind(this.resize, this));
	},
    
    onDomRefresh: function(){
        $('#breadcrumb').removeClass('visible-xs').hide();
        
        // init tooltip
        $('#map-toolbar a, .hastip').tooltip();
        
        this.initMap();
        
        // activate switch
        $('#map-container input.switch').bootstrapSwitch();
        $('#map-container input.switch').bootstrapSwitch('setSizeClass', 'switch-small');
        
        // activate scroller
        $("#map-container .scroller").scroller({
            trackMargin: 6
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
		
		$('.selectpicker').selectpicker({
			style: 'btn-special'
		});

    },
    
    onClose: function(e){
		// show breadcrumb on mobile
        $('#breadcrumb').addClass('visible-xs').show();
		
		// store current coordinates when changing view
		this.storeCoordinates();
		
		// unbind the namespaced events
        $(window).off("beforeunload.map");
		$(window).off("resize.map");
    },
    
    /* --- Nodeshot methods --- */
    
	resize: function(){
		setMapDimensions();
	},
	
	beforeunload: function(){
		// store current coordinates before leaving the page
		this.storeCoordinates();
	},
	
	/*
     * get current map coordinates (lat, lng, zoom)
     */
	getCoordinates: function(){
		var lat, lng, zoom;
		
		if (Nodeshot.preferences.mapMode == '2D') {
			lat = this.map.getCenter().lat;
			lng = this.map.getCenter().lng;
			zoom = this.map.getZoom()
		}
		else{
			var cartesian = Cesium.Ellipsoid.WGS84.cartesianToCartographic(
								this.map.scene.getCamera().position
							)
			
			lat = Math.degrees(cartesian.latitude),
			lng = Math.degrees(cartesian.longitude),
			zoom = 9
		}
		
		return {
			lat: lat,
			lng: lng,
			zoom: zoom
		}
	},
	
	/*
     * store current map coordinates in localStorage
     */
	storeCoordinates: function(){
		var coords = this.getCoordinates()
		
		Nodeshot.preferences.mapLat = coords.lat;
		Nodeshot.preferences.mapLng = coords.lng;
		Nodeshot.preferences.mapZoom = coords.zoom;
	},
	
	/*
     * get latest stored coordinates or default ones
     */
	rememberCoordinates: function(){
		return {
			lat: Nodeshot.preferences.mapLat || 42.12,
			lng: Nodeshot.preferences.mapLng || 12.45,
			zoom: Nodeshot.preferences.mapZoom || 9
		}
	},
	
    /*
     * add node procedure
     */
    addNode: function(e){
		var self = this,
			reopenLegend = false,
			dialog = this.ui.addNodeStep1,
            dialog_dimensions = dialog.getHiddenDimensions();
		
		// hide legend
		if (this.ui.legend.is(':visible')) {
			$('#map-legend').hide();
			//$('#map-legend .icon-close').trigger('click');
			//reopenLegend = true;
		}
		
		// hide toolbar and enlarge map
		this.ui.toolbar.hide();
		setMapDimensions();
        
		// show step1
        dialog.css({
            width: dialog_dimensions.width,
            right: 0
        });
        dialog.fadeIn(255);
        
		// cancel
		$('#add-node-step1 button').one('click', function(e){
            self.closeAddNode();
        });
		
		// on map click (only once)
		this.map.once('click', function(e){
			// drop marker on cliked point
			var marker = L.marker([e.latlng.lat, e.latlng.lng], {
				draggable: true
			}).addTo(self.map);
			self.newNodeMarker = marker;
			
			self.map.panTo(e.latlng);
			
			// hide step1
			dialog.hide();
			
			// show step2
            dialog = self.ui.addNodeStep2,
            dialog_dimensions = dialog.getHiddenDimensions();
            dialog.css({
                width: dialog_dimensions.width,
                right: 0
            });
            dialog.fadeIn(255);
			
			// bind cancel button once
			$('#add-node-step2 .btn-default').one('click', function(e){
				self.closeAddNode();
			});
			
			// add new node there
			$('#add-node-step2 .btn-success').one('click', function(e){
				dialog.fadeOut(255);
				self.ui.addNodeContainer.show().animate({
					width: '+70%'
				},
				{
					duration: 400,
					progress: function(){
						setMapDimensions();
						self.map.panTo(marker._latlng);
					},
					complete: function(){
						setMapDimensions();
						self.map.panTo(marker._latlng);
					}
				});
			});
		});
    },
	
	/*
     * submit new node
     */
	submitAddNode: function(e){
		e.preventDefault();
		
		var self = this,
			form = this.ui.addNodeForm;
			geojson = JSON.stringify(this.newNodeMarker.toGeoJSON().geometry),
			url = form.attr('action'),
			errorList = form.find('.error-list');
		
		form.find('.error-msg').text('').hide();
		form.find('.error').removeClass('error');
		errorList.html('').hide();
		
		$('#id_geometry').val(geojson);
		
		var data = form.serialize();
		
		// TODO: refactor this to use backbone and automatic validation
		$.post(url, data).done(function(){
			createModal({ message: 'new node added' });
			self.closeAddNode();
		}).error(function(http){
			var json = http.responseJSON;
			
			for (key in json) {
				var input = $('#id_'+key);
				if (input.length) {
					input.addClass('error');
					
					if (input.selectpicker) {
						input.selectpicker('setStyle');
					}
					
					var errorContainer = input.parent().find('.error-msg');
					
					if (!errorContainer.length) {
						errorContainer = input.parent().parent().find('.error-msg');
					}
					
					errorContainer.text(json[key]).fadeIn(255);
				}
				else{
					errorList.show();
					errorList.append('<li>' + json[key] + '</li>');
				}
			}
		});
	},
	
	/*
     * cancel addNode operation
     * resets normal map functions
     */
	closeAddNode: function(){
		var marker = this.newNodeMarker;
		// unbind click event
		this.map.off('click');
		
		var self = this,
			container = this.ui.addNodeContainer;
		
		if (container.is(':visible')) {
			container.animate({
				width: '0'
			},
			{
				duration: 400,
				progress: function(){
					setMapDimensions();
					if (marker) {
						self.map.panTo(marker._latlng);
					}
				},
				complete: function(){
					if (marker) {
						self.map.panTo(marker._latlng);
					}
					container.hide();
					setMapDimensions();
				}
			});
		}
		
		// reopen legend if necessary
		if (
			(Nodeshot.preferences.legendOpen === true || Nodeshot.preferences.legendOpen === "true") &&
			this.ui.legend.is(':hidden')
		) {
			this.ui.legend.show();
		}
		
		// show toolbar and adapt map width
		this.ui.toolbar.show();
		setMapDimensions();
		
		// hide step1 if necessary
		if (this.ui.addNodeStep1.is(':visible')) {
			this.ui.addNodeStep1.fadeOut(255);
		}
		
		// hide step2 if necessary
		if (this.ui.addNodeStep2.is(':visible')) {
			this.ui.addNodeStep2.fadeOut(255);
		}
		
		// remove marker if necessary
		if (marker) {
			this.map.removeLayer(marker);
		}
		
		setMapDimensions();
	},
    
    /*
     * show / hide toolbar panels
     */
    togglePanel: function(e){
        e.preventDefault();
	
        var button = $(e.currentTarget),
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
        this.ui.toolbarButtons.removeClass('active');
        
        if (panel.is(':hidden')) {
            var distance_from_top = button.offset().top - $('body > header').eq(0).outerHeight();
            panel.css('top', distance_from_top);
            
            // here we should use an event
            if (panel.hasClass('adjust-height')) {
                var preferences_height = this.$el.height() - distance_from_top -18;
                panel.height(preferences_height);
            }
            
            panel.show();
            panel.find('.scroller').scroller('reset');
            button.addClass('active');
            button.tooltip('disable');
        }
        else{
            panel.hide();
            button.tooltip('enable');
        }
    },
    
    /*
     * open or close legend
     */
    toggleLegend: function(e){
        e.preventDefault();
        
        var legend = this.ui.legend,
            button = this.ui.legendButton;
        
        if(legend.is(':visible')){
            legend.fadeOut(255);
            button.removeClass('disabled');
            button.tooltip('enable');
			Nodeshot.preferences.legendOpen = false;
        }
        else{
            legend.fadeIn(255);
            button.addClass('disabled');
            button.tooltip('disable').tooltip('hide');
			Nodeshot.preferences.legendOpen = true;
        }
    },
    
    /*
     * enable or disable something on the map
     * by clicking on its related legend control
     */
    toggleLegendControl: function(e){
        e.preventDefault();
	
        var li = $(e.currentTarget).parent();
        
        if (li.hasClass('disabled')) {
            li.removeClass('disabled');
        }
        else{
            li.addClass('disabled');
        }
    },
    
    /*
     * toggle map tool
     */
    toggleTool: function(e){
        e.preventDefault();
        var button = $(e.currentTarget),
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
    },
    
    /*
     * show / hide map toolbar on mobiles
     */
    toggleToolbar: function(e){
        e.preventDefault();
        $('#map-toolbar').toggle();
        setMapDimensions();
    },
    
    /*
     * initMap according to mode argument
     * mode can be undefined, 2D or 3D
     */
    initMap: function(mode){
        var button = this.ui.switchMapMode,
            unloadMethod,
            replacedString,
            replacerString,
            removedClass,
            addedClass,
			legend = this.ui.legend,
            buttonTitle = button.attr('data-original-title'),
            preferences = Nodeshot.preferences;
        
        // mode is either specified, or taken from localStorage or defaults to 2D
        mode = mode || preferences.mapMode || '2D';
        
        // ensure mode is either 2D or 3D, defaults to 2D
        if(mode !== '2D' && mode !== '3D'){
            mode = '2D'
        }
        
        if(mode === '2D'){
            unloadMethod = 'destroy';
            replacedString = '2D';
            replacerString = '3D';
            removedClass = 'right';
            addedClass = 'inverse';
        }
        else if(mode === '3D'){
            unloadMethod = 'remove';
            replacedString = '3D';
            replacerString = '2D';
            removedClass = 'inverse';
            addedClass = 'right';
        }
        
        // unload map if already initialized
        if(typeof(this.map) !== 'undefined'){
			// store current coordinates
			this.storeCoordinates();
			// unload map
			this.map[unloadMethod]();
			// clear any HTML in map container
			$('#map-js').html('');
        }
        
        setMapDimensions();
        
        // init map
        this.map = this['_initMap'+mode]();
        
        // switch icon
        button.removeClass('icon-'+replacedString.toLowerCase())
              .addClass   ('icon-'+replacerString.toLowerCase());
        
        // change tooltip message
        button.attr(
            'data-original-title',
            buttonTitle.replace(replacedString, replacerString)
        );
		
		if (preferences.legendOpen === false || preferences.legendOpen === 'false') {
			legend.hide();
		}
		else{
			this.ui.legendButton.addClass('disabled');
		}
		
        // adapt legend position and colors
        legend.removeClass(removedClass).addClass(addedClass);
        
        // store mapMode
        preferences.mapMode = mode;
    },
    
    /*
     * init 2D map
     * internal use only
     */
    _initMap2D: function(){
		var coords = this.rememberCoordinates(),
			map = L.map('map-js').setView([coords.lat, coords.lng], coords.zoom, {
				trackResize: true
			});
        // TODO: configurable tiles
        L.tileLayer('http://a.tiles.mapbox.com/v3/examples.map-9ijuk24y/{z}/{x}/{y}.png').addTo(map);
        return map;
    },
    
    /*
     * init 3D map
     * internal use only
     */
    _initMap3D: function(){
        var coords = this.rememberCoordinates(),
			map = new Cesium.CesiumWidget('map-js'),
			zoomLevels = [
				148500
			],
			flight = Cesium.CameraFlightPath.createAnimationCartographic(map.scene, {
				destination : Cesium.Cartographic.fromDegrees(coords.lng, coords.lat, 16500 * coords.zoom),
				duration: 0
			});
		
        map.centralBody.terrainProvider = new Cesium.CesiumTerrainProvider({
            url : 'http://cesiumjs.org/smallterrain'
        });
		
        map.scene.getAnimations().add(flight);
		
        return map;
    },
    
    /*
     * toggle 3D or 2D map
     */
    switchMapMode: function(e){
        e.preventDefault();
        // automatically determine which mod to use depending on the icon's button
        var mode = this.ui.switchMapMode.hasClass('icon-3d') ? '3D' : '2D';
        this.initMap(mode);
    }
});

Nodeshot.addRegions({
    body: '#body'
});

// localStorage check
Nodeshot.addInitializer(function(){
    Nodeshot.preferences = window.localStorage || {};
});

// init layout
Nodeshot.addInitializer(function(){
    
	Nodeshot.accountMenu = new AccountMenuView({ model: Nodeshot.currentUser });
	Nodeshot.accountMenu.render();
	
});

// init pages
Nodeshot.addInitializer(function(){
    Nodeshot.page = new Page();
    
    Nodeshot.page.on('sync', function(){
        Nodeshot.body.close();
        Nodeshot.body.show(new PageView({ model: Nodeshot.page }));
    });
    
    Nodeshot.page.on('error', function(model, http){
        if(http.status === 404){
            createModal({ message: 'the requested page was not found' });
        }
        else{
            createModal({ message: 'there was an error while retrieving the page' });
        }
    });
    
    Backbone.history.start();
});

var NodeshotController = {
    index: function(){
        Backbone.history.navigate('#pages/home', { trigger: true });
    },
    
    page: function(slug){
		toggleLoading('show');
		
        Nodeshot.page.set('slug', slug);
        Nodeshot.page.fetch();
        
        var link = $('#nav-bar a[href="#/pages/'+slug+'"]');
		
		// ensure no duplicate active links
		$('#nav-bar li').removeClass('active');
		
        if(link.length && link.parents('.dropdown').length){
            link.parents('.dropdown').addClass('active');
        }
        else{
            link.trigger('click');
        }
    },
    
    getMap: function(){
        Nodeshot.body.close();
        Nodeshot.body.show(new MapView());
        $('#nav-bar a[href="#/map"]').trigger('click');
    }
}

var NodeshotRouter = new Marionette.AppRouter({
    controller: NodeshotController,
    appRoutes: {
        "": "index",
        "pages/:slug": "page",
        "map": "getMap"
    }
});

$(document).ready(function($){
    Nodeshot.start();
	
	$('#js-signin-form').submit(function(e){
		e.preventDefault();
		var data = $(this).serialize();
		$.post('/api/v1/account/login/', data).error(function(){
			// TODO improve
			createModal({ message: 'incorrect login' })
		}).done(function(response){
			$('#signin-modal').modal('hide');
			Nodeshot.currentUser.set('username', response.username);
		});
	});
	
	$('#js-signup-form').submit(function(e){
		e.preventDefault();
		var data = $(this).serialize();
		$.post('/api/v1/profiles/', data).error(function(http){
			// TODO improve
			createModal({ message: JSON.stringify(http.responseJSON) });
		}).done(function(response){
			$('#signup-modal').modal('hide');
			createModal({ message: 'sent confirmation mail' });
		});
	});
	
	$('#js-signup-link').click(function(e){
		e.preventDefault();
		$('#signin-modal').modal('hide');
		$('#signup-modal').modal('show');
	});
	
	$('#js-signin-link').click(function(e){
		e.preventDefault();
		$('#signup-modal').modal('hide');
		$('#signin-modal').modal('show');
	});
	
	$('.js-dismiss').click(function(e){
		$(this).parents('.modal').modal('hide');
	});
});

var createModal = function(opts){
	var template_html = $('#modal-template').html(),
		options = $.extend({
			message: '',
			successMessage: 'ok',
			successAction: function(){ $('#tmp-modal').modal('hide') },
			defaultMessage: null,
			defaultAction: function(){ $('#tmp-modal').modal('hide') }
	}, opts);
	
	$('body').append(_.template(template_html, options));
	
	$('#tmp-modal').modal('show');
	
	$('#tmp-modal .btn-success').one('click', options.successAction);
	$('#tmp-modal .btn-default').one('click', options.defaultAction);
	
	$('#tmp-modal').one('hidden.bs.modal', function(e) {
		$('#tmp-modal').remove();
	})
};

var toggleLoading = function(operation){
	var loading = $('#loading');
	
	if (!loading.length) {
		$('body').append(_.template($('#loading-template').html(), {}));
		loading = $('#loading');
		
		var dimensions = loading.getHiddenDimensions();
		loading.outerWidth(dimensions.width);
		loading.css({ left: 0, margin: '0 auto' });
		
		// close loading
		$('#loading .icon-close').click(function(e){
			toggleLoading();
			if (Nodeshot.currentXHR) {
				Nodeshot.currentXHR.abort();
			}
		});
	}
	
	if (operation == 'show') {
		loading.fadeIn(255);
	}
	else if (operation == 'hide') {
		loading.fadeOut(255);
	}
	else{
		loading.fadeToggle(255);
	}
};

$(document).ajaxSend(function(event, xhr, settings) {
	toggleLoading('show');
	Nodeshot.currentXHR = xhr;
});

$(document).ajaxStop(function() {
	toggleLoading('hide');
});