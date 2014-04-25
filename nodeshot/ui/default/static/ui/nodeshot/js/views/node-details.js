var NodeDetailsView = Backbone.Marionette.ItemView.extend({
    name: 'NodeDetailsView',
    tagName: 'div',
    id: 'map-container',
    className: 'short-map',
    template: '#node-details-template',
    
    modelEvents: {
        'change': 'render'
    },
    
    events: {
        'click .icon-link': 'permalink'
    },

    onDomRefresh: function () {
        var slug = this.model.get('slug'),
            marker = Nodeshot.nodesNamed[slug],
            // init map on node coordinates and with high zoom (17)
            map = L.map('map-js', {
                trackResize: true,
                scrollWheelZoom: false
            }).setView(marker._latlng, 17);
        
        // TODO: FIXME & DRY
        marker = L.circleMarker(marker._latlng, marker.options);
        // add marker to map
        map.addLayer(marker);
        // move map up slightly
        map.panBy([0, 90], {
            animate: false
        });
        // TODO: configurable tiles
        // TODO: rename mapbox in osm
        this.mapBoxLayer = new L.tileLayer('//a.tiles.mapbox.com/v3/nemesisdesign.hcj0ha2h/{z}/{x}/{y}.png').addTo(map);
        this.map = map;

        $('body').attr('style', '').css({
            'overflow-x': 'hidden',
            'overflow-y': 'auto'
        });
        setMapDimensions();
        this.setMinHeight();
    },

    initialize: function () {
        // bind to namespaced events
        $(window).on("resize.node-details", _.bind(this.resize, this));
        
        // fetch details from DB
        this.model.fetch();
        
        this.listenTo(Nodeshot.currentUser, 'change', function(){ this.render() });
    },

    /*
     * unbind resize event when view is closed
     */
    onClose: function () {
        // unbind the namespaced events
        $(window).off("resize.node-details");
    },

    /*
     * resize window event
     */
    resize: function () {
        setMapDimensions();
        this.setMinHeight();
    },
    
    /*
     * set min-heigh css property on map-container div
     */
    setMinHeight: function () {
        var containerHeight = $('#map-container').outerHeight(),
            topDistance = parseInt($('#map-overlay-container').css('top').replace('px', ''));
        newMinHeight = containerHeight - topDistance;

        if (newMinHeight > 150) {
            $('#node-details').css('min-height', newMinHeight);
        }
    },
    
    /*
     * prompt permalink
     */
    permalink: function(e){
        e.preventDefault();
        var text = $(e.target).attr('data-text');
        window.prompt(text, window.location.href)
    }
});