(function(){
    'use strict';

    Ns.views.map.Layout = Marionette.LayoutView.extend({
        id: 'map-container',
        template: '#map-layout-template',

        regions: {
            content: '#map-js',
            legend: '#legend-js',
            panels: '#map-panels',
            toolbar: '#map-toolbar',
            add: '#map-add-node-js',
            details: '#map-details-js'
        },

        /**
         * show regions
         */
        onShow: function () {
            this.content.show(new Ns.views.map.Content({ parent: this }));
        },

        /**
         * loads map data
         */
        loadMap: function () {
            var options = { parent: this };
            this.toolbar.show(new Ns.views.map.Toolbar(options));
            this.panels.show(new Ns.views.map.Panels(options));
            this.legend.show(new Ns.views.map.Legend(options));
            this.content.currentView.initMapData();
        },

        /*
         * show add node view
         */
        addNode: function () {
            this.reset();
            // if not authenticated
            if (Ns.db.user.isAuthenticated() === false) {
                // show sign-in modal
                $('#signin-modal').modal('show');
                // listen to loggedin event and come back here
                this.listenToOnce(Ns.db.user, 'loggedin', this.addNode);
                return;
            }
            this.add.show(new Ns.views.map.Add({ parent: this }));
        },

        showNode: function(node) {
            this.details.show(new Ns.views.node.Detail({ model: node, parent: this }));
        },

        showEditNode: function(node) {
            // ensure is allowed to edit
            if (node.get('can_edit')) {
                this.showNode(node);
                this.details.currentView.edit();
            }
            // otherwise go back to details
            else {
                Ns.router.navigate('nodes/' + node.id, { trigger: true });
            }
        },

        /*
         * resets to view initial state
         */
        reset: function () {
            this.content.currentView.closeLeafletPopup();
            this.add.empty();
            this.details.empty();
        }

    }, {  // static methods

        show: function (method, args) {
            var view;
            if (typeof Ns.body.currentView === 'undefined' || !(Ns.body.currentView instanceof Ns.views.map.Layout)) {
                view = new Ns.views.map.Layout();
                Ns.body.show(view);
            }
            else {
                view = Ns.body.currentView;
                view.reset();
            }
            // call method on Layout view is specified
            if (method) { view[method].apply(view, args); }
        },

        /*
         * Resize page elements so that the leaflet map
         * takes most of the available space in the window
         */
        resizeMap: function () {
            var overlayContainer = $('#map-overlay-container'),
                height,
                selector,
                width,
                setWidth = false,
                body = $('body');
            body.css('overflow-x', 'hidden');
            // map
            if (!overlayContainer.length) {
                height = $(window).height() - $('body > header').height();
                selector = '#map-container, #map-toolbar';
            }
            // node details
            else {
                height = overlayContainer.height() + parseInt(overlayContainer.css('top'), 10);
                selector = '#map-container';
            }
            // set new height
            $(selector).height(height);
            width =  $(window).width();
            // take in consideration #map-add-node-js if visible
            if ($('#map-add-node-js').is(':visible')) {
                width = width - $('#map-add-node-js').outerWidth();
                setWidth = true;
            }
            // take in consideration map toolbar if visible
            else if ($('#map-toolbar').is(':visible')) {
                width = width - $('#map-toolbar').outerWidth();
                setWidth = true;
            }
            // set width only if map toolbar is showing
            if (setWidth){
                $('#map').width(width);
            }
            else{
                $('#map').attr('style', '');
            }
            body.attr('style', '');
            // TODO: this is ugly!
            // call leaflet invalidateSize() to download any gray spot
            if (Ns.body.currentView instanceof Ns.views.map.Layout &&
                Ns.body.currentView.content &&
                typeof Ns.body.currentView.content.currentView.map !== 'undefined'){
                Ns.body.currentView.content.currentView.map.invalidateSize();
            }
        }
    });

    Ns.views.map.Content = Marionette.ItemView.extend({
        template: false,

        collectionEvents: {
            // populate map as items are added to collection
            'add': 'addGeoModelToMap',
            // remove items from map when models are removed
            'remove': 'removeGeoModelFromMap'
        },

        initialize: function (options) {
            this.parent = options.parent;
            this.collection = new Ns.collections.Geo();
            this.popUpNodeTemplate = _.template($('#map-popup-node-template').html());
            // link tweak
            this.popUpLinkTemplate = _.template($('#map-popup-link-template').html());
            // reload data when user logs in or out
            this.listenTo(Ns.db.user, 'loggedin loggedout', this.reloadMapData);
            // bind to namespaced events
            $(window).on('resize.map', _.bind(this.resize, this));
            $(window).on('beforeunload.map', _.bind(this.storeMapProperties, this));
            // cleanup eventual alerts
            $.cleanupAlerts();
        },

        onShow: function () {
            this.initMap();
        },

        onDestroy: function () {
            // store current coordinates when changing view
            this.storeMapProperties();
            // unbind the namespaced events
            $(window).off('beforeunload.map');
            $(window).off('resize.map');
        },

        /*
         * get current map coordinates (lat, lng, zoom)
         */
        getMapProperties: function () {
            var latLng = this.map.getCenter();
            return {
                lat: latLng.lat,
                lng: latLng.lng,
                zoom: this.map.getZoom(),
                baseLayer: this.getCurrentBaseLayer()
            };
        },

        /*
         * store current map coordinates in localStorage
         */
        storeMapProperties: function () {
            localStorage.setObject('map', this.getMapProperties());
        },

        /*
         * get latest stored coordinates or default ones
         */
        rememberMapProperties: function () {
            return localStorage.getObject('map') || Ns.settings.map;
        },

        /*
         * resize window event
         */
        resize: function () {
            Ns.views.map.Layout.resizeMap();
            // when narrowing the window to medium-small size and toolbar is hidden and any panel is still visible
            if ($(window).width() <= 767 && $('#map-toolbar').is(':hidden') && $('.side-panel:visible').length) {
                // close panel
                $('.mask').trigger('click');
            }
        },

        /*
         * initialize leaflet map
         */
        initMap: function () {
            var self = this,
                memory = this.rememberMapProperties();
            this.resize();
            // init map
            this.map = $.loadDjangoLeafletMap();
            // remember last coordinates
            this.map.setView([memory.lat, memory.lng], memory.zoom, {
                trackResize: true
            });
            // store baseLayers
            this.baseLayers = {};
            _.each(this.map.layerscontrol._layers, function (baseLayer) {
                self.baseLayers[baseLayer.name] = baseLayer.layer;
                // keep name reference
                self.baseLayers[baseLayer.name].name = baseLayer.name;
            });
            // remember preferred baseLayer
            if (memory.baseLayer) {
                this.switchBaseLayer(memory.baseLayer);
            }
            // create (empty) clusters on map (will be filled by addGeoModelToMap)
            this.createClusters();
        },

        /**
         * changes base layer of the map, only if necessary
         * (calling the same action twice has no effect)
         */
        switchBaseLayer: function(name){
            // ignore if name is undefined
            if(typeof name === 'undefined'){ return; }
            // remove all base layers that are not relevant
            for (var key in this.baseLayers){
                if (this.baseLayers[key].name !== name) {
                    this.map.removeLayer(this.baseLayers[key]);
                }
            }
            // if the relevant layer is still not there add it
            if (!this.map.hasLayer(this.baseLayers[name])) {
                this.map.addLayer(this.baseLayers[name]);
            }
        },

        /**
         * returns name of the current map base layer
         */
        getCurrentBaseLayer: function () {
            for (var name in this.baseLayers){
                if (Boolean(this.baseLayers[name]._map)) {
                    return name;
                }
            }
            return null;
        },

        /*
         * loads data from API
         */
        initMapData: function () {
            Ns.changeTitle(gettext('Map'));
            Ns.menu.currentView.activate('map');
            Ns.track();
            Ns.state.onNodeClose = 'map';  // when a node-details is closed go back on map
            this.parent.toolbar.$el.addClass('enabled');
            this.resize();
            // load cached data if present
            if (Ns.db.geo.isEmpty() === false) {
                this.collection.add(Ns.db.geo.models);
                this.collection.trigger('ready');
            }
            // otherwise fetch from server
            else {
                this.fetchMapData();
            }
            // toggle legend group from map when visible attribute changes
            this.listenTo(Ns.db.legend, 'change:visible', this.toggleLegendGroup);
            // toggle layer data when visible attribute changes
            this.listenTo(Ns.db.layers, 'change:visible', this.toggleLayerData);
        },

        /*
         * fetch map data, merging changes if necessary
         */
        fetchMapData: function () {
            var self = this,
                // will contain fresh data
                geo = new Ns.collections.Geo(),
                // will be used to fetch data to merge in geo
                tmp = geo.clone(),
                additionalGeoJson = Ns.settings.additionalGeoJsonUrls,
                ready, fetch;
            // will be called when all sources have been fetched
            // we need to add 1 to account for the main geojson
            ready = _.after(additionalGeoJson.length + 1, function () {
                // reload models
                self.collection.remove(self.collection.models);
                self.collection.add(geo.models);
                // cache geo collection
                Ns.db.geo = self.collection;
                // trigger ready event
                self.collection.trigger('ready');
                // unbind event
                self.collection.off('sync', ready);
            });
            // fetch data and add it to collection
            fetch = function () {
                tmp.fetch().done(function () {
                    geo.add(tmp.models);
                    geo.trigger('sync');
                });
            };
            geo.on('sync', ready);
            // fetch data from API
            fetch();
            additionalGeoJson.forEach(function (url) {
                tmp._url = url;
                fetch();
            });
            // begin temporary tweak for links
            if (Ns.settings.links) {
                var links = new Ns.collections.Geo();
                links._url = Ns.url('links.geojson');
                links.fetch().done(function () {
                    geo.add(links.models);
                    geo.trigger('sync');
                });
            }
            // end tweak
        },

        /**
         * reload map data in the background
         */
        reloadMapData: function () {
            $.toggleLoading('hide');
            // disable loading indicator while data gets refreshed
            Ns.state.autoToggleLoading = false;
            // fetch data
            this.fetchMapData();
            // re-enable loading indicator once data is refreshed
            this.collection.once('ready', function(){ Ns.state.autoToggleLoading = true });
        },

        /**
         * prepare empty Leaflet.MarkerCluster objects
         */
        createClusters: function () {
            var self = this,
                legend;
            // loop over each legend item
            Ns.db.legend.forEach(function (legendModel) {
                legend = legendModel.toJSON();
                // group markers in clusters
                var cluster = new L.MarkerClusterGroup({
                    iconCreateFunction: function (cluster) {
                        var count = cluster.getChildCount(),
                            // determine size with the last number of the exponential notation
                            // 0 for < 10, 1 for < 100, 2 for < 1000 and so on
                            size = count.toExponential().split('+')[1];
                        return L.divIcon({
                            html: count,
                            className: 'cluster cluster-size-' + size + ' marker-' + this.cssClass
                        });
                    },
                    polygonOptions: {
                        fillColor: legend.fill_color,
                        stroke: legend.stroke_width > 0,
                        weight: legend.stroke_width,
                        color: legend.stroke_color,
                        opacity: 0.4
                    },
                    cssClass: legend.slug,
                    chunkedLoading: true,
                    showCoverageOnHover: true,
                    zoomToBoundsOnClick: true,
                    removeOutsideVisibleBounds: true,
                    disableClusteringAtZoom: Ns.settings.disableClusteringAtZoom,
                    maxClusterRadius: Ns.settings.maxClusterRadius
                });
                // store reference
                legendModel.cluster = cluster;
                // show cluster only if corresponding legend item is visible
                if(legend.visible){
                    self.map.addLayer(cluster);
                }
            });
        },

        /**
         * returns options for the initialization of tooltip for leaflet layers
         */
        tooltipOptions: function(data) {
            return {
                container: '#map-js',
                placement: 'auto top',
                title: data.name,
                delay: { show: 600, hide: 0 }
            }
        },

        /**
         * adds a geo model to its cluster
         * binds popup
         * called whenever a model is added to the collection
         */
        addGeoModelToMap: function (model) {
            var self = this,
                leafletLayer = model.get('leaflet'),
                legend = model.get('legend'),
                data = model.toJSON(),
                layer = Ns.db.layers.get(data.layer),
                // link tweak
                template = model._type === 'node' ? this.popUpNodeTemplate : this.popUpLinkTemplate;
            // bind leaflet popup
            leafletLayer.bindPopup(template(data));
            // mouse over / out events
            leafletLayer.on({
                mouseover: function (e) {
                    var l = e.target,
                        type = l.feature.geometry.type;
                    // opacity to 1
                    l.setStyle({ fillOpacity: 1 });
                    // bring to front
                    if (!L.Browser.ie && !L.Browser.opera && type === 'Point') {
                        l.bringToFront({ fillOpacity: 1 });
                    }
                },
                mouseout: function (e) {
                    e.target.setStyle({ fillOpacity: Ns.settings.leafletOptions.fillOpacity });
                },
                // when popup opens, change the URL fragment
                popupopen: function (e) {
                    var fragment = Backbone.history.fragment;
                    // do this only if in general map view
                    if (fragment.indexOf('map') >= 0 && fragment.indexOf('nodes') < 0) {
                        Ns.router.navigate('map/' + data.slug);
                    }
                    // destroy container to avoid the chance that the tooltip
                    // might appear while showing the leaflet popup
                    $(e.target._container).tooltip('destroy');
                },
                // when popup closes
                popupclose: function (e) {
                    // (and no new popup opens)
                    // URL fragment goes back to initial state
                    var fragment = Backbone.history.fragment;
                    setTimeout(function () {
                        // do this only if in general map view
                        if (self.map._popup === null && fragment.indexOf('map') >= 0 && fragment.indexOf('nodes') < 0) {
                            Ns.router.navigate('map');
                        }
                    }, 100);
                    // rebind tooltip (it has been destroyed in popupopen event)
                    $(e.target._container).tooltip(self.tooltipOptions(data));
                },
                add: function(e){
                    // create tootlip when leaflet layer is added to the view
                    $(e.target._container).tooltip(self.tooltipOptions(data));
                },
                remove: function(e){
                    // ensure tooltip is removed when layer is removed from map
                    $(e.target._container).tooltip('destroy');
                }
            });
            // show on map only if corresponding nodeshot layer is visible
            if (layer && layer.get('visible')) {
                legend.cluster.addLayer(leafletLayer);
                // avoid covering points
                if (leafletLayer._map && leafletLayer.feature.geometry.type !== 'Point') {
                    leafletLayer.bringToBack();
                }
            }
        },

        /**
         * remove geo model from its cluster
         * called whenever a model is removed from the collection
         */
        removeGeoModelFromMap: function (model) {
            var cluster = model.get('legend').cluster;
            cluster.removeLayer(model.get('leaflet'));
        },

        /*
         * show / hide from map items of a legend group
         */
        toggleLegendGroup: function (legend, visible) {
            var method = (visible) ? 'addLayer' : 'removeLayer';
            this.map[method](legend.cluster);
        },

        /*
        * show / hide from map items of a legend group
        */
        toggleLayerData: function (layer, visible) {
            var geo = this.collection,
                method = (visible) ? 'addLayers' : 'removeLayers',
                l;
            Ns.db.legend.forEach(function(legend){
                l = geo.whereCollection({ legend: legend, layer: layer.id }).pluck('leaflet');
                legend.cluster[method](l);
            });
            // needed to recalculate stats on legend
            this.trigger('layer-toggled');
        },

        /*
         * Open leaflet popup of the specified element
         */
        openLeafletPopup: function (id) {
            var collection = this.collection,
                self = this,
                leafletLayer;
            // open leaflet pop up if ready
            if (collection.length && typeof collection !== 'undefined') {
                try {
                    leafletLayer = this.collection.get(id).get('leaflet');
                } catch (e) {
                    $.createModal({
                        message: id + ' ' + gettext('not found'),
                        onClose: function () {
                            Ns.router.navigate('map');
                        }
                    });
                    return;
                }
                try {
                    leafletLayer.openPopup();
                }
                // clustering plugin hides leafletLayers when clustered or outside viewport
                // so we have to zoom in and center the map
                catch (e){
                    this.map.fitBounds(leafletLayer.getBounds());
                    leafletLayer.openPopup();
                }
            }
            // if not ready wait for map.collectionReady and call again
            else {
                this.collection.once('ready', function () {
                    self.openLeafletPopup(id);
                });
            }
            return;
        },

        /*
         * Close leaflet popup if open
         */
        closeLeafletPopup: function () {
            var popup = $('#map-js .leaflet-popup-close-button');
            if (popup.length) {
                popup.get(0).click();
            }
        },

        /*
         * Go to specified latitude and longitude
         */
        goToLatLng: function (latlng, zoom) {
            latlng = latlng.split(',')
            latlng = L.latLng(latlng[0], latlng[1]);
            var self = this,
                marker = L.marker(latlng);
            // used in search address feature
            if (!zoom) {
                marker.addTo(this.map);
                zoom = 18;
            }
            // go to marker and zoom in
            this.map.setView(latlng, zoom);
            // fade out marker
            if (typeof(marker) !== 'undefined' && this.map.hasLayer(marker)) {
                $([marker._icon, marker._shadow]).fadeOut(4000, function () {
                    self.map.removeLayer(marker);
                });
            }
        }
    });

    Ns.views.map.Legend = Marionette.ItemView.extend({
        id: 'map-legend',
        className: 'overlay inverse',
        template: '#map-legend-template',

        ui: {
            'close': 'a.icon-close'
        },

        events: {
            'click @ui.close': 'toggleLegend',
            'click li a': 'toggleGroup'
        },

        collectionEvents: {
            // automatically render when toggling group or recounting
            'change:visible counted': 'render'
        },

        initialize: function (options) {
            this.parent = options.parent;
            this.collection = Ns.db.legend;
            this.legendButton = this.parent.toolbar.currentView.ui.legendButton;
            // display count in legend
            this.listenTo(this.parent.content.currentView.collection, 'ready', this.count);
            this.listenTo(this.parent.content.currentView, 'layer-toggled', this.count);
        },

        onRender: function () {
            // default is true
            if (localStorage.getObject('legendOpen') === false) {
                this.$el.hide();
            } else {
                this.legendButton.addClass('disabled');
            }
        },

        /*
         * calculate counts
         */
        count: function () {
            this.collection.forEach(function (legend) {
                legend.set('count', legend.cluster.getLayers().length);
            });
            // trigger once all legend items have been counted
            this.collection.trigger('counted');
        },

        /*
         * open or close legend
         */
        toggleLegend: function (e) {
            e.preventDefault();

            var legend = this.$el,
                button = this.legendButton,
                open;

            if (legend.is(':visible')) {
                legend.fadeOut(255);
                button.removeClass('disabled');
                button.tooltip('enable');
                open = false;
            } else {
                legend.fadeIn(255);
                button.addClass('disabled');
                button.tooltip('disable').tooltip('hide');
                open = true;
            }

            localStorage.setItem('legendOpen', open);
        },

        /*
         * enable or disable something on the map
         * by clicking on its related legend control
         */
        toggleGroup: function (e) {
            e.preventDefault();
            var status = $(e.currentTarget).attr('data-status'),
                item = this.collection.get(status);
            item.set('visible', !item.get('visible'));
        }
    });

    Ns.views.map.Toolbar = Marionette.ItemView.extend({
        template: '#map-toolbar-template',

        ui: {
            'buttons': 'a',
            'switchMapMode': '#btn-map-mode',
            'legendButton': '#btn-legend',
            'toolsButton': 'a.icon-tools',
            'prefButton': 'a.icon-config',
            'layersControl': 'a.icon-layer-2'
        },

        events: {
            'click .icon-pin-add': 'addNode',
            'click @ui.buttons': 'togglePanel',
            'click @ui.switchMapMode': 'switchMapMode',
            // siblings events
            'click @ui.legendButton': 'toggleLegend'
        },

        initialize: function (options) {
            this.parent = options.parent;
        },

        onRender: function () {
            var self = this;
            // init tooltip
            this.ui.buttons.tooltip();
            // correction for map tools
            this.ui.toolsButton.click(function (e) {
                var button = $(this),
                    prefButton = self.ui.prefButton;
                if (button.hasClass('active')) {
                    prefButton.tooltip('disable');
                } else {
                    prefButton.tooltip('enable');
                }
            });
            // correction for map-filter
            this.ui.layersControl.click(function (e) {
                var button = $(this),
                    otherButtons = self.$el.find('a.icon-config, a.icon-3d, a.icon-tools');
                if (button.hasClass('active')) {
                    otherButtons.tooltip('disable');
                } else {
                    otherButtons.tooltip('enable');
                }
            });
        },

        /*
         * show / hide map toolbar on narrow screens
         */
        toggleToolbar: function (e) {
            e.preventDefault();
            // shortcut
            var toolbar = this.parent.toolbar.$el,
                target = $(e.currentTarget);
            // show toolbar
            if (toolbar.is(':hidden')) {
                // just add display:block
                // which overrides css media-query
                toolbar.show();
                // overimpose on toolbar
                target.css('right', '-60px');
            }
            // hide toolbar
            else {
                // instead of using jQuery.hide() which would hide the toolbar also
                // if the user enlarged the screen, we clear the style attribute
                // which will cause the toolbar to be hidden only on narrow screens
                toolbar.attr('style', '');
                // close any open panel
                if ($('.side-panel:visible').length) {
                    $('.mask').trigger('click');
                }
                // eliminate negative margin correction
                target.css('right', '0');
            }
            Ns.views.map.Layout.resizeMap();
        },

        /*
         * proxy to call add node
         */
        addNode: function (e) {
            e.preventDefault();
            this.parent.addNode();
        },

        /*
         * redirects to Ns.views.map.Panels
         */
        toggleLegend: function (e) {
            this.parent.legend.currentView.toggleLegend(e);
        },

        /*
         * redirects to Ns.views.map.Panels
         */
        togglePanel: function (e) {
            this.parent.panels.currentView.togglePanel(e);
        },

        /*
         * toggle 3D or 2D map
         */
        switchMapMode: function (e) {
            e.preventDefault();
            $.createModal({message: gettext('not implemented yet')});
        }
    });

    Ns.views.map.Panels = Marionette.ItemView.extend({
        template: '#map-panels-template',

        ui: {
            'switches': 'input.switch',
            'scrollers': '.scroller',
            'selects': '.selectpicker',
            'tools': '.tool',
            'distance': '#fn-map-tools .icon-ruler',
            'area': '#fn-map-tools .icon-select-area',
            'elevation': '#fn-map-tools .icon-elevation-profile'
        },

        events: {
            'click #fn-map-tools .notImplemented': 'toggleToolNotImplemented',
            'click @ui.distance': 'toggleDistance',
            'click @ui.area': 'toggleArea',
            'click @ui.elevation': 'toggleElevation',
            'click #toggle-toolbar': 'toggleToolbar',
            'change .js-base-layers input': 'switchBaseLayer',
            'switch-change #fn-map-layers .toggle-layer-data': 'toggleLayer',
            'switch-change #fn-map-layers .toggle-legend-data': 'toggleLegend'
        },

        initialize: function (options) {
            this.parent = options.parent;
            this.mapView = this.parent.content.currentView;
            this.toolbarView = this.parent.toolbar.currentView;
            this.toolbarButtons = this.toolbarView.ui.buttons;
            // listen to legend change event
            this.listenTo(Ns.db.legend, 'change:visible', this.syncLegendSwitch);
            this.populateBaseLayers();
            // init tools
            if (Ns.settings.mapTools) {
                this.tools = {
                    'distance': new L.Polyline.Measure(this.mapView.map),
                    'area': new L.Polygon.Measure(this.mapView.map),
                    'elevation': new L.Polyline.Elevation(this.mapView.map)
                };
            }
        },

        // populate this.baseLayers
        populateBaseLayers: function () {
            var self = this,
                layer;
            this.baseLayers = [];
            // get ordering of baselayers django-leaflet options
            this.mapView.map.options.djoptions.layers.forEach(function (layerConfig) {
                layer = self.mapView.baseLayers[layerConfig[0]];
                self.baseLayers.push({
                    checked: Boolean(layer._map),  // if _map is not null it means this is the active layer
                    name: layer.name
                });
            });
        },

        serializeData: function(){
            return {
                'layers': Ns.db.layers.toJSON(),
                'legend': Ns.db.legend.toJSON(),
                'baseLayers': this.baseLayers
            }
        },

        onRender: function () {
            this.ui.tools.tooltip();
            // activate switch
            this.ui.switches.bootstrapSwitch().bootstrapSwitch('setSizeClass', 'switch-small');
            // activate scroller
            this.ui.scrollers.scroller({
                trackMargin: 6
            });
            // fancy selects
            this.ui.selects.selectpicker({
                style: 'btn-special'
            });
        },

        /*
         * show / hide toolbar panels
         */
        togglePanel: function (e) {
            e.preventDefault();

            var button = $(e.currentTarget),
                panelId = button.attr('data-panel'),
                panel = $('#' + panelId),
                self = this,
                // determine distance from top
                distanceFromTop = button.offset().top - $('body > header').eq(0).outerHeight(),
                preferencesHeight;

            // if no panel return here
            if (!panel.length) {
                return;
            }

            // hide any open tooltip
            $('#map-toolbar .tooltip').hide();
            panel.css('top', distanceFromTop);

            // adjust height of panel if marked as 'adjust-height'
            if (panel.hasClass('adjust-height')) {
                preferencesHeight = $('#map-toolbar').height() - distanceFromTop - 18;
                panel.height(preferencesHeight);
            }

            panel.fadeIn(25, function () {
                panel.find('.scroller').scroller('reset');
                button.addClass('active');
                button.tooltip('hide').tooltip('disable');
                // create a mask for easy closing
                $.mask(panel, function (e) {
                    // close function
                    if (panel.is(':visible')) {
                        panel.hide();
                        self.toolbarButtons.removeClass('active');
                        button.tooltip('enable');
                        // if clicking again on the same button avoid reopening the panel
                        if ($(e.target).attr('data-panel') === panelId) {
                            e.stopPropagation();
                            e.preventDefault();
                        }
                    }
                });
            });
        },

        toggleToolNotImplemented: function (e) {
            e.preventDefault();
            $.createModal({ message: gettext('not implemented yet') });
            return false;
        },

        /*
         * toggle map tool
         */
        toggleToolButton: function (e) {
            var button = $(e.currentTarget),
                active_buttons = $('#fn-map-tools .tool.active');
            // if activating a tool
            if (!button.hasClass('active')) {
                // deactivate any other
                active_buttons.trigger('click');
                button.addClass('active')
                      .tooltip('hide')
                      .tooltip('disable');
                return true;
            // deactivate
            } else {
                button.removeClass('active')
                      .tooltip('enable')
                      .trigger('blur');
                return false;
            }
        },

        toggleDrawTool: function (toolName, e) {
            var result = this.toggleToolButton(e),
                tool = this.tools[toolName];
            if (result) {
                tool.enable();
                // if tool is disabled with ESC or other ways
                // sync the nodeshot UI
                tool.once('disabled', function () {
                    this.toggleToolButton(e);
                }, this);
            }
            else {
                tool.off('disabled');
                tool.disable();
            }
        },

        toggleDistance: function (e) {
            this.toggleDrawTool('distance', e);
        },

        toggleArea: function (e) {
            this.toggleDrawTool('area', e);
        },

        toggleElevation: function (e) {
            this.toggleDrawTool('elevation', e);
        },

        drawElevation: function (geojson) {
            // local vars
            var points = [],
                self = this;
            // the elevation API expects latitude, longitude, so we have to reverse our coords
            geojson.geometry.coordinates.forEach(function(point){
                points.push(point.reverse());
            });
            // query the elevation API
            $.getJSON(Ns.url('elevation/'), {
                // output is '<lat>,<lng>|<lat>,<lng>|<lat>,<lng'
                path: points.join('|')
            }).done(function(geojson){
                // close tools panel
                $('.mask').trigger('click');
                // create control
                var el = L.control.elevation({
                        position: 'bottomright',
                        width: 1020,
                        height: 299,
                        margins: {
                            top: 25,
                            right: 40,
                            bottom: 40,
                            left: 70
                        },
                    });
                el.addTo(self.mapView.map);
                var geojsonLayer = L.geoJson(geojson, {
                    onEachFeature: el.addData.bind(el),
                    style: function () {
                        return {
                            color: '#e6a1b3',
                            opacity: 0.7
                        }
                    }
                }).addTo(self.mapView.map);
                var close = $('<a href="#" class="icon-close"></a>');
                $('#map-js .elevation.leaflet-control').append('<a href="#" class="icon-close"></a>');
                $('#map-js .elevation.leaflet-control .icon-close').one('click', function (e) {
                    e.preventDefault();
                    self.mapView.map.removeControl(el);
                    self.mapView.map.removeLayer(geojsonLayer);
                })
            });
        },

        /*
         * proxy to Ns.views.map.Toolbar.toggleToolbar
         */
        toggleToolbar: function (e) {
            this.toolbarView.toggleToolbar(e);
        },

        /**
         * changes base layer of the map
         * proxy to Ns.views.map.Content.switchBaseLayer
         */
        switchBaseLayer: function (event) {
            this.mapView.switchBaseLayer($(event.target).attr('data-name'));
        },

        /**
         * hide / show layer data on map
         */
        toggleLayer: function (event, data) {
            var layer = Ns.db.layers.get(data.el.attr('data-slug'));
            layer.set('visible', data.value);
        },

        /**
         * hide / show legend data on map
         */
        toggleLegend: function(event, data){
            this.parent.legend.currentView.$('a[data-status=' + data.el.attr('data-slug') + ']').trigger('click');
        },

        /**
         * sync legend state with switches in panel
         */
        syncLegendSwitch: function(legend, state){
            var input = this.$('#map-control-legend-' + legend.get('slug'));
            if(input.bootstrapSwitch('state') !== state){
                // second parameter indicates wheter to skip triggering switch event
                input.bootstrapSwitch('toggleState', true);
            }
        }
    });

    Ns.views.map.Add = Marionette.ItemView.extend({
        template: '#map-add-node-template',
        tagName: 'article',

        ui: {
            'formContainer': '#add-node-form-container'
        },

        events: {
            'click #add-node-form-container .btn-default': 'destroy',
            'submit #add-node-form-container form': 'submitAddNode'
        },

        initialize: function (options) {
            this.parent = options.parent;
            // references to objects of other views
            this.ext = {
                legend: this.parent.legend.$el,
                toolbar: this.parent.toolbar.$el,
                map: this.parent.content.$el,
                leafletMap: this.parent.content.currentView.map,
                geo: this.parent.content.currentView.collection,
                step1: $('#add-node-step1'),
                step2: $('#add-node-step2')
            };
            // elements that must be hidden
            this.hidden =  $().add(this.ext.legend)
                              .add(this.ext.toolbar)
                              .add(this.ext.map.find('.leaflet-control-attribution'));
            // needed for toggleLeafletLayers
            this.dimmed = false;
        },

        serializeData: function(){
            return { 'layers': Ns.db.layers.toJSON() };
        },

        onShow: function () {
            Ns.router.navigate('map/add');
            Ns.changeTitle(gettext('Add node'));
            Ns.track();
            // go to step1 when collection is ready
            if (this.ext.geo.length){
                this.step1();
            }
            else {
                this.listenToOnce(this.ext.geo, 'ready', this.step1);
            }
            // dynamic form
            this.form = new Backbone.Form({
                model: new Ns.models.Node(),
                submitButton: gettext('Add node')
            }).render();
            this.ui.formContainer.html(this.form.$el);
            this.$('input[type=checkbox]').bootstrapSwitch().bootstrapSwitch('setSizeClass', 'switch-small');
            this.$('select').selectpicker({style: 'btn-special' });
        },

        /*
         * when the view is destroyed the map is taken backto its original state
         */
        onBeforeDestroy: function () {
            this.closeAddNode();
            // change url fragment but only if we are still on the map
            if (Backbone.history.fragment.substr(0, 3) == 'map'){
                Ns.router.navigate('map');
            }
        },

        /*
         * proxy to Ns.views.map.Layout.resizeMap
         */
        resizeMap: function() {
            Ns.views.map.Layout.resizeMap();
        },

        /*
         * hide elements that are not needed when adding a new node
         * show them back when finished
         */
        toggleHidden: function(){
            this.hidden.toggle();
            this.resizeMap();
            this.toggleLeafletLayers();
        },

        /*
         * dim out leaflet layers from map when adding a new node
         * reset default options when finished
         * clusters are toggled (hidden and shown back) through an additional style tag in <head>
         * because clusters are re-rendered whenever the map is moved or resized so inline changes
         * do not persist when resizing or moving
         */
        toggleLeafletLayers: function () {
            var leafletOptions = Ns.settings.leafletOptions,
                tmpOpacity = leafletOptions.temporaryOpacity,
                clusterCss = $('#add-node-cluster-css'),
                dimOut = !this.dimmed,
                leaflet;
            // dim out or reset all leaflet layers
            this.ext.geo.forEach(function(model){
                leaflet = model.get('leaflet');
                if (dimOut) {
                    leaflet.options.opacity = tmpOpacity;
                    leaflet.options.fillOpacity = tmpOpacity;
                    leaflet.setStyle(leaflet.options);
                }
                else {
                    leaflet.options.opacity = leafletOptions.opacity;
                    leaflet.options.fillOpacity = leafletOptions.fillOpacity;
                    leaflet.setStyle(leaflet.options);
                }
            });
            if (clusterCss.length === 0) {
                $('head').append('<style id="add-node-cluster-css">.cluster{ display: none }</style>');
            }
            else{
                clusterCss.remove();
            }
            // change dimmed state
            this.dimmed = dimOut;
        },

        /*
         * step1 of adding a new node
         */
        step1: function (e) {
            var self = this,
                dialog = this.ext.step1,
                dialog_dimensions = dialog.getHiddenDimensions();
            // hide toolbar and enlarge map
            this.toggleHidden();
            // show step1
            dialog.css({
                width: dialog_dimensions.width+2,
                right: 0
            });
            dialog.fadeIn(255);
            // cancel
            this.ext.step1.find('button').one('click', function () { self.destroy() });
            // on map click (only once)
            this.ext.leafletMap.once('click', function (e) {
                dialog.fadeOut(255);
                self.step2(e);
            });
        },

        step2: function (e) {
            var self = this,
                dialog = this.ext.step2,
                dialog_dimensions = dialog.getHiddenDimensions(),
                map = this.ext.leafletMap,
                callback,
                latlng,
                // draggable marker
                marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable: true}).addTo(map);
            // keep a global reference
            this.newNodeMarker = marker;
            // set address on form
            this.setAddressFromLatLng(e.latlng);
            this.form.setValue('geometry', JSON.stringify(marker.toGeoJSON()));
            this.setGeometryFromMarker(marker);
            // update address when moving the marker
            marker.on('dragend', function (event) {
                latlng = event.target.getLatLng();
                self.setAddressFromLatLng(latlng);
                self.setGeometryFromMarker(event.target);
                map.panTo(latlng);
            });
            // zoom in to marker
            map.setView(marker.getLatLng(), 18, { animate: true });
            // show step2
            dialog = self.ext.step2,
            dialog_dimensions = dialog.getHiddenDimensions();
            dialog.css({
                width: dialog_dimensions.width+2,
                right: 0
            });
            dialog.fadeIn(255);
            // bind cancel button once
            this.ext.step2.find('.btn-default').one('click', function () { self.destroy() });
            // bind confirm button once
            this.ext.step2.find('.btn-success').one('click', function () {
                callback = function () {
                    self.resizeMap();
                    map.panTo(marker._latlng);
                };
                dialog.fadeOut(255);
                // show form with a nice animation
                self.parent.add.$el.show().animate({ width: '+70%'}, {
                    duration: 400,
                    progress: callback,
                    complete: callback
                });
            });
        },

        /*
         * submit new node
         */
        submitAddNode: function (e) {
            e.preventDefault();
            var self = this,
                form = this.form,
                geojson = JSON.stringify(this.newNodeMarker.toGeoJSON().geometry),
                errorList = this.$('.error-list'),
                node = form.model,
                errors = form.commit(),
                geo;
            if (errors) {
                return false;
            }
            this.$('.help-block').text('').hide();
            this.$('.error').removeClass('error');
            this.$('.has-error').removeClass('has-error');
            errorList.html('').hide();
            node.save().done(function () {
                // convert to Geo model
                node = new Ns.models.Geo(node.toJSON());
                // add to geo collection
                self.ext.geo.add(node);
                // destroy this view
                self.destroy();
                // open new node popup
                node.get('leaflet').openPopup();
            }).error(function (http) {
                // TODO: make this reusable
                var json = http.responseJSON,
                    key, input, errorContainer;
                for (key in json) {
                    input = self.$('input[name=' + key + ']');
                    if (input.length) {
                        input.addClass('error');
                        errorContainer = input.parents('.form-group').find('.help-block');
                        errorContainer.text(json[key])
                                      .removeClass('hidden')
                                      .addClass('has-error')
                                      .fadeIn(255);
                    } else {
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
        closeAddNode: function () {
            var marker = this.newNodeMarker,
                container = this.parent.add.$el,
                map = this.ext.leafletMap,
                self = this,
                resetToOriginalState = function () {
                    container.hide();
                    // show hidden elements again
                    self.toggleHidden();
                };
            // unbind click events
            map.off('click');
            this.ext.step1.find('button').off('click');
            this.ext.step2.find('.btn-default').off('click');
            this.ext.step2.find('.btn-success').off('click');
            // remove marker if necessary
            if (marker) {
                map.removeLayer(marker);
            }
            // hide step1 if necessary
            if (this.ext.step1.is(':visible')) {
                this.ext.step1.fadeOut(255);
            }
            // hide step2 if necessary
            if (this.ext.step2.is(':visible')) {
                this.ext.step2.fadeOut(255);
            }
            // if container is visible
            if (container.is(':visible')) {
                // hide it with a nice animation
                container.animate({ width: '0' }, {
                    duration: 400,
                    progress: function () {
                        self.resizeMap();
                        if (marker) { map.panTo(marker._latlng); }
                    },
                    complete: resetToOriginalState
                });
            }
            // reset original state
            else{
                resetToOriginalState();
            }
        },

        /*
         * retrieve address from latlng through OSM Nominatim service
         * and set it on the add node form
         */
        setAddressFromLatLng: function (latlng) {
            var self = this;
            $.geocode({
                lat: latlng.lat,
                lon: latlng.lng,
                callback: function(result){
                    self.form.setValue('address', result.display_name);
                }
            });
        },

        /**
         * set geometry on model from marker geojson
         */
         setGeometryFromMarker: function (marker) {
             this.form.setValue('geometry', JSON.stringify(marker.toGeoJSON().geometry));
         }
    });
})();
