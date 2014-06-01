var MapView = Backbone.Marionette.ItemView.extend({
    name: 'MapView',
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
        'click #map-toolbar .icon-search': 'removeAddressFoundMarker',
        'submit #fn-search-address form': 'searchAddress',
        'click @ui.toolbarButtons': 'togglePanel',
        'click @ui.legendTogglers': 'toggleLegend',
        'click #map-legend li a': 'toggleLegendControl',
        'click #fn-map-tools .tool': 'toggleTool',
        'click #toggle-toolbar': 'toggleToolbar',
        'click @ui.switchMapMode': 'switchMapMode',
        'click #add-node-form .btn-default': 'closeAddNode',
        'submit #add-node-form': 'submitAddNode',
        'switch-change #fn-map-layers .toggle-layer-data': 'toggleLayerData'
    },

    initialize: function () {
        // bind to namespaced events
        $(window).on("beforeunload.map", _.bind(this.beforeunload, this));
        $(window).on("resize.map", _.bind(this.resize, this));

        this.resetDataContainers();
        Nodeshot.onNodeClose = '#/map';
    },

    onDomRefresh: function () {
        $('#breadcrumb').removeClass('visible-xs').hide();

        // init tooltip
        $('#map-toolbar a').tooltip();

        this.initMap();

        // activate switch
        $('#map-container input.switch').bootstrapSwitch();
        $('#map-container input.switch').bootstrapSwitch('setSizeClass', 'switch-small');

        // activate scroller
        $("#map-container .scroller").scroller({
            trackMargin: 6
        });

        // correction for map tools
        $('#map-toolbar a.icon-tools').click(function (e) {
            var button = $(this),
                preferences_button = $('#map-toolbar a.icon-config');
            if (button.hasClass('active')) {
                preferences_button.tooltip('disable');
            } else {
                preferences_button.tooltip('enable');
            }
        });

        // correction for map-filter
        $('#map-toolbar a.icon-layer-2').click(function (e) {
            var button = $(this),
                other_buttons = $('a.icon-config, a.icon-3d, a.icon-tools', '#map-toolbar');
            if (button.hasClass('active')) {
                other_buttons.tooltip('disable');
            } else {
                other_buttons.tooltip('enable');
            }
        });

        $('.selectpicker').selectpicker({
            style: 'btn-special'
        });

        // if only 1 layer available
        // preselect it in the add node form
        var layer_options = $('#id_layer option[value]');
        if(layer_options.length === 1){
            var value = layer_options.eq(0).val();
            $('#id_layer').selectpicker('val', value)
        }
    },

    onClose: function (e) {
        // show breadcrumb on mobile
        $('#breadcrumb').addClass('visible-xs').show();

        // store current coordinates when changing view
        this.storeCoordinates();

        // unbind the namespaced events
        $(window).off("beforeunload.map");
        $(window).off("resize.map");
    },

    /* --- Nodeshot methods --- */

    // reset containers with pointers to markers and other map objects
    resetDataContainers: function () {
        Nodeshot.nodes = [];
        Nodeshot.nodesNamed = [];
        Nodeshot.clusters = [];
        _.each(Nodeshot.statuses, function (status) {
            status.nodes = [];
        });
    },

    resize: function () {
        setMapDimensions();

        // when narrowing the window to medium-small size
        if($(window).width() <= 767){
            // if any side-panel remains open
            var panels = $('.side-panel:visible');
            if(panels.length){
                // trigger click on header to close it
                $('body>header').trigger('click');
            }
        }
    },

    beforeunload: function () {
        // store current coordinates before leaving the page
        this.storeCoordinates();
    },

    /*
     * get current map coordinates (lat, lng, zoom)
     */
    getCoordinates: function () {
        var lat, lng, zoom;

        if (Nodeshot.preferences.mapMode == '2D') {
            lat = this.map.getCenter().lat;
            lng = this.map.getCenter().lng;
            zoom = this.map.getZoom()
        } else {
            var cartesian = Cesium.Ellipsoid.WGS84.cartesianToCartographic(
                this.map.scene.getCamera().position
            )

            lat = Math.degrees(cartesian.latitude),
            lng = Math.degrees(cartesian.longitude),
            zoom = 9;
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
    storeCoordinates: function () {
        var coords = this.getCoordinates()

        Nodeshot.preferences.mapLat = coords.lat;
        Nodeshot.preferences.mapLng = coords.lng;
        Nodeshot.preferences.mapZoom = coords.zoom;
    },

    /*
     * get latest stored coordinates or default ones
     */
    rememberCoordinates: function () {
        return {
            lat: Nodeshot.preferences.mapLat || Nodeshot.MAP_CENTER[0],
            lng: Nodeshot.preferences.mapLng || Nodeshot.MAP_CENTER[1],
            zoom: Nodeshot.preferences.mapZoom || Nodeshot.MAP_ZOOM
        }
    },

    /*
     * add node procedure
     */
    addNode: function (e) {
        var self = this,
            reopenLegend = false,
            dialog = this.ui.addNodeStep1,
            dialog_dimensions = dialog.getHiddenDimensions();

        if (!Nodeshot.currentUser.get('username')) {
            $('#signin-modal').modal('show');
            return;
        }

        // hide legend
        if (this.ui.legend.is(':visible')) {
            $('#map-legend').hide();
        }

        // hide toolbar and enlarge map
        this.ui.toolbar.hide();
        setMapDimensions();
        this.toggleMarkersOpacity('fade');

        // show step1
        dialog.css({
            width: dialog_dimensions.width,
            right: 0
        });
        dialog.fadeIn(255);

        // cancel
        $('#add-node-step1 button').one('click', function (e) {
            self.closeAddNode();
        });

        // on map click (only once)
        this.map.once('click', function (e) {
            // drop marker on cliked point
            var marker = L.marker([e.latlng.lat, e.latlng.lng], {
                draggable: true
            }).addTo(self.map);
            self.newNodeMarker = marker;

            self.getAddress(e.latlng)

            self.newNodeMarker.on('dragend', function (event) {
                var marker = event.target;
                var result = marker.getLatLng();
                self.getAddress(result)
            });
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
            $('#add-node-step2 .btn-default').one('click', function (e) {
                self.closeAddNode();
            });

            // add new node there
            $('#add-node-step2 .btn-success').one('click', function (e) {
                dialog.fadeOut(255);
                self.ui.addNodeContainer.show().animate({
                    width: '+70%'
                }, {
                    duration: 400,
                    progress: function () {
                        setMapDimensions();
                        self.map.panTo(marker._latlng);
                    },
                    complete: function () {
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
    submitAddNode: function (e) {
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
        $.post(url, data).done(function () {
            // TODO: fire custom event here
            createModal({
                message: 'new node added'
            });
            self.closeAddNode(function () {
                // show added node
                // TODO: improve ugly code
                loadNodeData();
                self.resetDataContainers();
                self.loadMapData();
                self.clusterizeMarkers();
            });
        }).error(function (http) {
            var json = http.responseJSON;

            for (key in json) {
                var input = $('#id_' + key);
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
    closeAddNode: function (callback) {
        var marker = this.newNodeMarker;
        // unbind click event
        this.map.off('click');

        var self = this,
            container = this.ui.addNodeContainer;

        if (container.is(':visible')) {
            container.animate({
                width: '0'
            }, {
                duration: 400,
                progress: function () {
                    setMapDimensions();
                    if (marker) {
                        self.map.panTo(marker._latlng);
                    }
                },
                complete: function () {
                    if (marker) {
                        self.map.panTo(marker._latlng);
                    }
                    container.hide();
                    setMapDimensions();

                    if (callback && typeof (callback) === 'function') {
                        callback();
                    }
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
        this.toggleMarkersOpacity();

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
     * partially fade out or reset markers from the map
     * used when adding a node
     */
    toggleMarkersOpacity: function (action) {
        var tmpOpacity = 0.3;

        // loop over nodes
        for (var i = 0, len = Nodeshot.nodes.length; i < len; i++) {
            var node = Nodeshot.nodes[i];

            if (action === 'fade') {
                node.options.opacity = tmpOpacity;
                node.options.fillOpacity = tmpOpacity;
                node.setStyle(node.options);
            } else {
                node.setStyle(node.defaultOptions);
            }
        }
    },

    /*
     * show / hide toolbar panels
     */
    togglePanel: function (e) {
        e.preventDefault();

        var button = $(e.currentTarget),
            panel_id = button.attr('data-panel'),
            panel = $('#' + panel_id),
            self = this;

        // if no panel return here
        if (!panel.length) {
            return;
        }

        // hide any open tooltip
        $('#map-toolbar .tooltip').hide();

        var distance_from_top = button.offset().top - $('body > header').eq(0).outerHeight();
        panel.css('top', distance_from_top);

        // here we should use an event
        if (panel.hasClass('adjust-height')) {
            var preferences_height = this.$el.height() - distance_from_top - 18;
            panel.height(preferences_height);
        }

        panel.fadeIn(25, function(){
            panel.find('.scroller').scroller('reset');
            button.addClass('active');
            button.tooltip('disable');

            // clicking anywhere else closes the panel
            $('#map-toolbar, body > header, #map > div:not(.side-panel)').one('click', function(e){
                if(panel.is(':visible')){
                    panel.hide();
                    self.ui.toolbarButtons.removeClass('active');
                    button.tooltip('enable');
                    // if clicking again on the same button avoid reopening the panel
                    if($(e.target).attr('data-panel') == panel_id){
                        e.stopPropagation();
                        e.preventDefault();
                    }
                }
            });
        });
    },

    /*
     * open or close legend
     */
    toggleLegend: function (e) {
        e.preventDefault();

        var legend = this.ui.legend,
            button = this.ui.legendButton;

        if (legend.is(':visible')) {
            legend.fadeOut(255);
            button.removeClass('disabled');
            button.tooltip('enable');
            Nodeshot.preferences.legendOpen = false;
        } else {
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
    toggleLegendControl: function (e) {
        e.preventDefault();

        var a = $(e.currentTarget),
            li = a.parent(),
            status = a.attr('data-status');

        if (li.hasClass('disabled')) {
            li.removeClass('disabled');
            this.toggleMarkers('show', status);
        } else {
            li.addClass('disabled');
            this.toggleMarkers('hide', status);
        }
    },

    /*
     * hide or show markers from map
     * TODO: this is cumbersome and needs semplification
     */
    toggleMarkers: function (action, status) {
        // local vars / shortcuts
        var functionName,
            cluster = Nodeshot.statuses[status].cluster,
            markers = Nodeshot.statuses[status].nodes,
            visibleStatuses = Nodeshot.preferences.visibleStatuses.split(',');
        
        // mark each marker visibility depending on visible layers
        _.forEach(markers, function(marker){
            marker.visible = action === 'show';
        });
        
        if(action === 'show'){
            // add layer to map
            this.map.addLayer(cluster);
            // show
            this.showVisibleClusters();
            // remember choice
            if(visibleStatuses.indexOf(status) < 0){
                visibleStatuses.push(status);
            }
        }
        else if(action === 'hide'){
            this.map.removeLayer(cluster);
            // remember choice
            var index = visibleStatuses.indexOf(status);
            if(index > -1){
                visibleStatuses.splice(index, 1);
            }
        }
        
        // remember choice
        Nodeshot.preferences.visibleStatuses = visibleStatuses;
    },

    /*
     * toggle map tool
     */
    toggleTool: function (e) {
        e.preventDefault();
        var button = $(e.currentTarget),
            active_buttons = $('#fn-map-tools .tool.active');

        if (!button.hasClass('active')) {
            // deactivate any other
            active_buttons.removeClass('active');
            active_buttons.tooltip('enable');

            button.addClass('active');
            button.tooltip('hide');
            button.tooltip('disable');
        } else {
            button.removeClass('active');
            button.tooltip('enable');
        }
    },

    /*
     * show / hide map toolbar on mobiles
     */
    toggleToolbar: function (e) {
        e.preventDefault();
        this.ui.toolbar.toggle();
        // if toolbar has just been hidden
        if(this.ui.toolbar.is(':hidden')){
            // close any open panel
            if($('.side-panel:visible').length){
                $('body>header').trigger('click');
            }
        }
        setMapDimensions();
    },

    /*
     * initMap according to mode argument
     * mode can be undefined, 2D or 3D
     */
    initMap: function (mode) {
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
        if (mode !== '2D' && mode !== '3D') {
            mode = '2D'
        }

        if (mode === '2D') {
            unloadMethod = 'destroy';
            replacedString = '2D';
            replacerString = '3D';
            removedClass = 'right';
            addedClass = 'inverse';
        } else if (mode === '3D') {
            unloadMethod = 'remove';
            replacedString = '3D';
            replacerString = '2D';
            removedClass = 'inverse';
            addedClass = 'right';
        }

        // unload map if already initialized
        if (typeof (this.map) !== 'undefined') {
            // store current coordinates
            this.storeCoordinates();
            // unload map
            this.map[unloadMethod]();
            // clear any HTML in map container
            $('#map-js').html('');
        }

        setMapDimensions();

        // init map
        this.map = this['_initMap' + mode]();

        // switch icon
        button.removeClass('icon-' + replacedString.toLowerCase())
            .addClass('icon-' + replacerString.toLowerCase());

        // change tooltip message
        button.attr(
            'data-original-title',
            buttonTitle.replace(replacedString, replacerString)
        );

        if (preferences.legendOpen === false || preferences.legendOpen === 'false') {
            legend.hide();
        } else {
            this.ui.legendButton.addClass('disabled');
        }

        // adapt legend position and colors
        legend.removeClass(removedClass).addClass(addedClass);

        // store mapMode
        preferences.mapMode = mode;

        // load data
        this.loadMapData();
        this.clusterizeMarkers();
        this.rememberVisibleStatuses();
    },

    /*
     * init 2D map
     * internal use only
     */
    _initMap2D: function () {
        var coords = this.rememberCoordinates(),
            map = L.map('map-js').setView([coords.lat, coords.lng], coords.zoom, {
                trackResize: true
            });
        this.osmLayer = new L.tileLayer(Nodeshot.TILESERVER_URL).addTo(map);

        return map;
    },

    /*
     * init 3D map
     * internal use only
     */
    _initMap3D: function () {
        var coords = this.rememberCoordinates(),
            map = new Cesium.CesiumWidget('map-js'),
            zoomLevels = [
                148500
            ],
            flight = Cesium.CameraFlightPath.createAnimationCartographic(map.scene, {
                destination: Cesium.Cartographic.fromDegrees(coords.lng, coords.lat, 16500 * coords.zoom),
                duration: 0
            });

        map.centralBody.terrainProvider = new Cesium.CesiumTerrainProvider({
            url: 'http://cesiumjs.org/smallterrain'
        });

        map.scene.getAnimations().add(flight);

        return map;
    },

    loadMapData: function () {
        var options = {
            fill: true,
            lineCap: 'circle',
            radius: 6,
            opacity: 1,
            fillOpacity: 0.7
        },
            popUpTemplate = _.template($('#map-popup-template').html()),
            preferences = Nodeshot.preferences;
        
        // visible statuses
        preferences.visibleStatuses = preferences.visibleStatuses || _.keys(Nodeshot.statuses)
        // visible layers
        preferences.visibleLayers = preferences.visibleLayers || Nodeshot.layersSlugs;

        // loop over each layer
        for (var i = 0; i < Nodeshot.layers.length; i++) {
            var layer = Nodeshot.layers[i],
                visibleStatuses = Nodeshot.preferences.visibleStatuses.split(','),
                visibleLayers = Nodeshot.preferences.visibleLayers.split(',');

            var leafletLayer = L.geoJson(layer.nodes_geojson, {
                style: function (feature) {
                    var status = Nodeshot.statuses[feature.properties.status];
                    options.fillColor = status.fill_color;
                    options.stroke = status.stroke_width > 0;
                    options.weight = status.stroke_width;
                    options.color = status.stroke_color;
                    options.className = 'marker-' + status.slug;
                    return options
                },
                onEachFeature: function (feature, layer) {
                    // add slug in properties
                    feature.properties.slug = feature.id;
                    // bind leaflet popup
                    layer.bindPopup(popUpTemplate(feature.properties));
                },
                pointToLayer: function (feature, latlng) {
                    var marker = L.circleMarker(latlng, options);
                    
                    // marks as visible or not depending on preferences
                    if(visibleStatuses.indexOf(feature.properties.status) >= 0 && visibleLayers.indexOf(feature.properties.layer) >= 0){
                        marker.visible = true;
                    }
                    else{
                        marker.visible = false;
                    }

                    marker.on('click', function (e) {
                        Backbone.history.navigate('#/map/' + feature.id);
                    });

                    Nodeshot.statuses[feature.properties.status].nodes.push(marker);
                    Nodeshot.nodes.push(marker);
                    Nodeshot.nodesNamed[feature.id] = marker;
                    return marker
                }
            });
        }
    },

    clusterizeMarkers: function () {
        // loop over each status
        for (var key in Nodeshot.statuses) {

            var status = Nodeshot.statuses[key],
                // group marker in layerGroup
                leafletLayer = L.layerGroup(status.nodes);

            // TODO: this is ugly!
            $('head').append("\
                <style type='text/css'>\
                .marker-" + key + " {\
                    background-color:" + status.fill_color + ";\
                    color:" + status.text_color + ";\
                    border: " + status.stroke_width + "px solid " + status.stroke_color + ";\
                }\
                </style>\
            ");

            // group markers in clusters
            var group = new L.MarkerClusterGroup({
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
                    fillColor: status.fill_color,
                    stroke: status.stroke_width > 0,
                    weight: status.stroke_width,
                    color: status.stroke_color
                },
                chunkedLoading: true,
                showCoverageOnHover: true,
                zoomToBoundsOnClick: true,
                removeOutsideVisibleBounds: true,
                // TODO: make these configurable
                disableClusteringAtZoom: 12,
                maxClusterRadius: 90,
                singleMarkerMode: true,
                // custom option
                cssClass: key
            });

            group.status = key;

            // store for future reference
            status.cluster = group;
            Nodeshot.clusters.push(group);

            // show visible markers
            this.showVisibleMarkers(group, status.nodes);

            // Adds cluster to map
            this.map.addLayer(group);
        }
    },

    /*
     * toggle 3D or 2D map
     */
    switchMapMode: function (e) {
        e.preventDefault();
        createModal({message:'not implemented yet'});
        return
        // automatically determine which mod to use depending on the icon's button
        var mode = this.ui.switchMapMode.hasClass('icon-3d') ? '3D' : '2D';
        this.initMap(mode);
    },

    showVisibleMarkers: function (cluster, markers) {
        for (var i = 0, len = markers.length; i < len; i++) {
            var marker = markers[i];
            if (marker.visible) {
                cluster.addLayer(marker);
            }
        }
    },

    showVisibleClusters: function () {
        var self = this;
        _.each(Nodeshot.clusters, function (cluster) {
            cluster.clearLayers();
            // show visible markers
            self.showVisibleMarkers(cluster, Nodeshot.statuses[cluster.status].nodes);
        });
    },

    /*
     * show or hide markers of a layer
     */
    toggleLayerData: function (e, data) {
        var input = $(e.currentTarget),
            slug = input.attr('data-slug'),
            visibleLayers = Nodeshot.preferences.visibleLayers.split(','),
            visibleStatuses = Nodeshot.preferences.visibleStatuses.split(',');

        // loop over nodes
        for (var i = 0, len = Nodeshot.nodes.length; i < len; i++) {
            var node = Nodeshot.nodes[i];

            // show marker if layer corresponds and status is visible
            if (node.feature.properties.layer === slug && _.contains(visibleStatuses, node.feature.properties.status)) {
                // mark appropiately
                node.visible = data.value;
            }
        }
        
        this.showVisibleClusters();
        
        // remember choice
        if(data.value){
            if(visibleLayers.indexOf(slug) < 0){
                visibleLayers.push(slug);
            }
        }
        else{
            var index = visibleLayers.indexOf(slug);
            if(index > -1){
                visibleLayers.splice(index, 1);
            }
        }
        Nodeshot.preferences.visibleLayers = visibleLayers;
    },

    /*
     * Get Address using OSM Nominatim service
     */
    getAddress: function (latlng) {

        //var latlngToString = latlng.toString();
        var arrayLatLng = latlng.toString().split(",");
        var lat = arrayLatLng[0].slice(7);
        var lng = arrayLatLng[1].slice(0, -1);
        var url = 'http://nominatim.openstreetmap.org/reverse?format=json&lat=' + lat + '&lon=' + lng + '&zoom=18&addressdetails=0';
        $.ajax({
            async: true,
            url: url,
            dataType: 'json',
            success: function (response) {
                var address = response.display_name;
                $("#id_address").val(address);
            }
        });
    },

    searchAddress: function (e) {
        e.preventDefault();

        this.removeAddressFoundMarker()
        var self = this
        var searchString = $("#fn-search-address input").val()
        var url = "http://nominatim.openstreetmap.org/search?format=json&q=" + searchString
        $.ajax({
            async: true,
            url: url,
            dataType: 'json',
            success: function (response) {
                if (_.isEmpty(response)) {
                    createModal({
                        message: 'Address not found'
                    });
                } else {
                    var firstPlaceFound = (response[0]); // first place returned from OSM is displayed on map
                    var lat = parseFloat(firstPlaceFound.lat);
                    var lng = parseFloat(firstPlaceFound.lon);
                    var latlng = L.latLng(lat, lng);
                    self.addressFoundMarker = L.marker(latlng)
                    self.addressFoundMarker.addTo(self.map);
                    self.map.setView(latlng, 16);
                }
            }
        });
    },

    removeAddressFoundMarker: function () {
        if (typeof (this.addressFoundMarker) != "undefined") {
            this.map.removeLayer(this.addressFoundMarker)
        }
    },
    
    /*
     * remember hide/show nodes based on status choices
     */
    rememberVisibleStatuses: function(){
        var visibleStatuses = Nodeshot.preferences.visibleStatuses.split(',');
        
        // find out which statuses have to be disabled in the legend
        // use underscore array difference
        toDisable = _.difference(_.keys(Nodeshot.statuses), visibleStatuses)
        
        // add disabled class
        toDisable.forEach(function(status){
            $('#map-legend a[data-status="'+status+'"]').parents('li').addClass('disabled');
        });
    }
});
