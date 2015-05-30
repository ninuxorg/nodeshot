L.Polyline.Measure = L.Draw.Polyline.extend({
    addHooks: function() {
        L.Draw.Polyline.prototype.addHooks.call(this);
        if (this._map) {
            this._markerGroup = new L.LayerGroup();
            this._map.addLayer(this._markerGroup);
            this._markers = [];
            this._map.on('click', this._onClick, this);
            this._startShape();
        }
    },

    removeHooks: function () {
        L.Draw.Polyline.prototype.removeHooks.call(this);
        this._clearHideErrorTimeout();
        //!\ Still useful when control is disabled before any drawing (refactor needed?)
        this._map.off('mousemove', this._onMouseMove);
        this._clearGuides();
        this._container.style.cursor = '';
        this._removeShape();
        this._map.off('click', this._onClick, this);
    },

    _startShape: function() {
        this._drawing = true;
        this._poly = new L.Polyline([], this.options.shapeOptions);
        this._container.style.cursor = 'crosshair';
        this._updateTooltip();
        this._map.on('mousemove', this._onMouseMove, this);
    },

    _finishShape: function () {
        this._drawing = false;
        this._cleanUpShape();
        this._clearGuides();
        this._updateTooltip();
        this._map.off('mousemove', this._onMouseMove, this);
        this._container.style.cursor = '';
    },

    _removeShape: function() {
        if (!this._poly)
            return;
        this._map.removeLayer(this._poly);
        delete this._poly;
        this._markers.splice(0);
        this._markerGroup.clearLayers();
    },

    _onClick: function(e) {
        if (!this._drawing && e.originalEvent.target.id !== 'btn-elevation-profile') {
            this._removeShape();
            this._startShape();
            return;
        }
        else if (!this._drawing && e.originalEvent.target.id === 'btn-elevation-profile') {
            this._elevationProfile();
        }
    },

    _getTooltipText: function() {
        var labelText = L.Draw.Polyline.prototype._getTooltipText.call(this),
            elevLabel,
            elevButton;
        if (!this._drawing) {
            elevLabel = gettext('elevation profile');
            labelText.text = '<button class="btn btn-default" id="btn-elevation-profile">' + elevLabel + '</button>';
        }
        return labelText;
    },

    _elevationProfile: function () {
        Ns.body.currentView.panels.currentView.drawElevation(this._poly.toGeoJSON());
        this.disable();
    }
});

L.Polyline.Elevation = L.Polyline.Measure.extend({
    _getTooltipText: function() {
        var labelText = L.Draw.Polyline.prototype._getTooltipText.call(this);
        if (!this._drawing) {
            labelText.text = '';
        }
        return labelText;
    },

    _finishShape: function () {
        L.Polyline.Measure.prototype._finishShape.call(this);
        this._elevationProfile();
    },
});

L.Polygon.Measure = L.Draw.Polygon.extend({
    options: { showArea: true },

    addHooks: function() {
        L.Draw.Polygon.prototype.addHooks.call(this);
        if (this._map) {
            this._markerGroup = new L.LayerGroup();
            this._map.addLayer(this._markerGroup);
            this._markers = [];
            this._map.on('click', this._onClick, this);
            this._startShape();
        }
    },

    removeHooks: function () {
        L.Draw.Polygon.prototype.removeHooks.call(this);
        this._clearHideErrorTimeout();
        //!\ Still useful when control is disabled before any drawing (refactor needed?)
        this._map.off('mousemove', this._onMouseMove);
        this._clearGuides();
        this._container.style.cursor = '';
        this._removeShape();
        this._map.off('click', this._onClick, this);
    },

    _startShape: function() {
        this._drawing = true;
        this._poly = new L.Polygon([], this.options.shapeOptions);
        this._container.style.cursor = 'crosshair';
        this._updateTooltip();
        this._map.on('mousemove', this._onMouseMove, this);
    },

    _finishShape: function () {
        this._drawing = false;
        this._cleanUpShape();
        this._clearGuides();
        this._updateTooltip();
        this._map.off('mousemove', this._onMouseMove, this);
        this._container.style.cursor = '';
    },

    _removeShape: function() {
        if (!this._poly)
            return;
        this._map.removeLayer(this._poly);
        delete this._poly;
        this._markers.splice(0);
        this._markerGroup.clearLayers();
    },

    _onClick: function(e) {
        if (!this._drawing) {
            this._removeShape();
            this._startShape();
            return;
        }
    },

    _getTooltipText: function() {
        var labelText = L.Draw.Polygon.prototype._getTooltipText.call(this);
        if (!this._drawing) {
            labelText.text = '';
            labelText.subtext = this._getArea();
        }
        return labelText;
    },

    _getArea: function() {
        var latLng = [],
            geodisc;
        for(var i=0, len=this._markers.length; i < len; i++) {
            latLng.push(this._markers[i]._latlng);
        }
        geodisc = L.GeometryUtil.geodesicArea(latLng);
        return L.GeometryUtil.readableArea(geodisc, true);
    }
});
