function Geojson(json, lng, lat) {
    var Feature = function () {
        this.type = "Feature",
        this.geometry = {
            "type": "Point",
        }
        this.properties = {}
    }
    this.type = "FeatureCollection",
    this.features = [];
    this.load = function (json, lng, lat) {
        for (var i in json) {
            //console.log('test' + i)
            if (json[i][lng] && json[i][lat]) {
                var feature = new Feature;
                feature.geometry.coordinates = [json[i][lng], json[i][lat]]
                feature.properties = json[i]
                this.features.push(feature)
            }
        }
    }
}