var Nodeshot = new Backbone.Marionette.Application();

var Page = Backbone.Model.extend({
    urlRoot : '/api/v1/pages/',
    idAttribute: 'slug',
    
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
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
        'toolbarButtons': '#map-toolbar a',
        'legendTogglers': '#btn-legend, #map-legend a.icon-close'
    },
    
    events: {
        'click #map-toolbar .icon-pin-add': 'addNode',
        'click @ui.toolbarButtons': 'togglePanel',
        'click @ui.legendTogglers': 'toggleLegend',
        'click #map-legend li a': 'toggleLegendControl',
        'click #fn-map-tools .tool': 'toggleTool',
        'click #toggle-toolbar': 'toggleToolbar',
        'click #btn-toggle-3D': 'toggle3D'
    },
    
    onDomRefresh: function(){
        $('#breadcrumb').removeClass('visible-xs').hide();
        
        setMapDimensions();
        this.map = L.mapbox.map('map-js', 'examples.map-9ijuk24y').setView([42.12, 12.45], 9);
        
        // activate switch
        $('#map-container input.switch').bootstrapSwitch();
        $('#map-container input.switch').bootstrapSwitch('setSizeClass', 'switch-small');
        
        // activate scroller
        $("#map-container .scroller").scroller({
            trackMargin: 6
        });
        
        // init tooltip
        $('#map-toolbar a, .hastip').tooltip();
        
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
    },
    
    onClose: function(e){
        $('#breadcrumb').addClass('visible-xs').show();
    },
    
    /* --- Nodeshot methods --- */
    
    /*
     * add node procedure
     */
    addNode: function(e){
        $('#map-legend .icon-close').trigger('click');
    
        var dialog = $('#step1'),
            dialog_dimensions = dialog.getHiddenDimensions();
        
        dialog.css({
            width: dialog_dimensions.width,
            right: 0
        });
        
        // vertically align to center
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
            dialog.fadeIn(255);
        });
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
     * toggle 3D or 2D map
     */
    toggle3D: function(e){
        e.preventDefault();
        var button = $(e.currentTarget);
        
        // toggle 3D
        if(button.hasClass('icon-3d')){
            this.map.remove();
            $('#map-js').html('');
            this.map = new Cesium.CesiumWidget('map-js');
            this.map.centralBody.terrainProvider = new Cesium.CesiumTerrainProvider({
                url : 'http://cesiumjs.org/smallterrain'
            });
            // switch icon
            button.removeClass('icon-3d').addClass('icon-2d');
            // change tooltip message
            button.attr('data-original-title', button.attr('data-original-title').replace('3D', '2D'));
            // adapt legend position and colors
            $('#map-legend').removeClass('inverse').addClass('right');
        }
        else{
            this.map.destroy();
            $('#map-js').html('');
            this.map = L.mapbox.map('map-js', 'examples.map-9ijuk24y').setView([42.12, 12.45], 9);
            // switch icon
            button.removeClass('icon-2d').addClass('icon-3d');
            // change tooltip message
            button.attr('data-original-title', button.attr('data-original-title').replace('2D', '3D'));
            // adapt legend position and colors
            $('#map-legend').addClass('inverse').removeClass('right');
        }
        
        setMapDimensions();
    }
});

Nodeshot.addRegions({
    body: '#body'
});

Nodeshot.addInitializer(function(){
    Nodeshot.page = new Page();
    
    Nodeshot.page.on('sync', function(){
        Nodeshot.body.close();
        Nodeshot.body.show(new PageView({ model: Nodeshot.page }));
    });
    
    Nodeshot.page.on('error', function(model, http){
        if(http.status === 404){
            alert('the requested page was not found');
        }
        else{
            alert('there was an error while retrieving the page');
        }
    });
    
    Backbone.history.start();
});

var NodeshotController = {
    index: function(){
        Backbone.history.navigate('#pages/home', { trigger: true });
    },
    
    page: function(slug){
        Nodeshot.page.set('slug', slug);
        Nodeshot.page.fetch();
        
        var link = $('#nav-bar a[href="#/pages/'+slug+'"]');
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
});