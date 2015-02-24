(function(){
    'use strict';

    Ns.views.layer.Detail = Marionette.ItemView.extend({
        tagName: 'div',
        id: 'layer-details-container',
        template: '#layer-details-template',

        events: {
            'click .icon-link': 'permalink',
            'click .icon-mail': 'contact'
        },

        initialize: function (options) {
            this.model = Ns.db.layers.get(options.slug);
            // title
            Ns.changeTitle(this.model.get('name'));
            // menu element
            Ns.menu.currentView.activate('layers');
            // analytics
            Ns.track();
            // show
            Ns.body.show(this);
        },

        onShow: function () {
            this.map = $.loadDjangoLeafletMap();
            var area = this.model.get('area'),
                center = this.model.get('center'),
                areaIsPoint = area['type'] == 'Point',
                areaLayer = this.geoJsonToLayer(area, areaIsPoint ? null : 0.3),
                centerLayer = this.geoJsonToLayer(center);
            // add area and fit map size according to it
            this.map.addLayer(areaLayer);
            // if area is a Point, just center the view but don't zoom
            if (areaIsPoint) {
                this.map.setView(centerLayer.getLatLng());
            }
            // if area is not a point, use fit bounds
            else {
                this.map.fitBounds(areaLayer.getBounds());
            }
        },

        /**
         * takes geojson object as input
         * returns leaflet layer
         */
        geoJsonToLayer: function (geojson, fillOpacity) {
            var options = _.clone(Ns.settings.leafletOptions);
            options.fillOpacity = fillOpacity || options.fillOpacity;
            return L.geoJson(geojson, {
                style: function (feature) {
                    return options;
                },
                // used only for points
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, options);
                }
            }).getLayers()[0];
        },

        /*
         * prompt permalink
         */
        permalink: function(e){
            e.preventDefault();
            var text = $(e.target).attr('data-text');
            window.prompt(text, window.location.href);
        },

        contact: function (e) {
            if(!Ns.db.user.isAuthenticated()){
                e.preventDefault();
                $('#signin-modal').modal('show');
                return;
            }
        }
    });
})();
