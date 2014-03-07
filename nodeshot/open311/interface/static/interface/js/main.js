var csrftoken = $.getCookie('csrftoken');
var markerToRemove //If users insert a new marker previous one has to be deleted from map
var nodeRatingAVG // Rating data has to be globally available for rating plugin to correctly work
var markerMap = {} //Object holding all nodes'slug and a reference to their marker
//Map initialization
var map = L.map('map').setView([41.87, 12.49], 8);
//var legend = L.control({position: 'bottomleft'});
//
//legend.onAdd = function (map) {
//
//    var div = L.DomUtil.create('div','mapLegend'),
//        open_color = statuses.open.fill_color;
//        closed_color = statuses.closed.fill_color;
//
//
//    // loop through our density intervals and generate a label with a colored square for each interval
//    
//        div.innerHTML = "<span style='color:"+open_color+"'>Open requests</span><br>"
//        div.innerHTML += "<span style='color:"+closed_color+"'>Closed requests</span><br>"
//
//
//    return div;
//};



//legend.addTo(map);
var osmLayer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
//Uncomment for Google maps. Must be checked if it works in IE
var googleHybrid = new L.Google('HYBRID');
var googleMap = new L.Google('ROADMAP');
var googleSat = new L.Google();

//OSM layer added to map
osmLayer.addTo(map);
map.on('click', onMapClick);
var popup = L.popup();

//Layer insert on map
var overlaymaps = {};


//Load data from server
var layers = getData(window.__BASEURL__ + 'api/v1/layers/'); //layers
var geojsonlayers = getData(window.__BASEURL__ + 'api/v1/layers.geojson'); //layers' area


/* Definition of color for layer's visualization
 * Custom icon of status "Attivo" for layer is used for this purpose.
 * It would be better ( and faster) to have a default generic color property for layers
 * and use status icons when working on nodes
 * */

for (var i in layers) {
    //{
    //    var message = '';
    //    var layerColors = getData(window.__BASEURL__ + 'api/v1/layers/' + layers[i].slug + '/status_icons');
    //    if (layerColors.status_icons.length == 0) {
    //        message += layers[i].slug + ',';
    //    }
    //    for (var j in layerColors.status_icons) {
    //        if (layerColors.status_icons[j].status == "Attivo") {
    //            layers[i].color = layerColors.status_icons[j].background_color;
    //            createlayersCSS(layers[i].slug, layers[i].color);
    //            console.log('layercss creato per ' + layers[i].slug)
    //            for (var k in geojsonlayers.features) {
    //                var geolayerSlug = geojsonlayers.features[k].properties.slug
    //                if (geolayerSlug == layers[i].slug) {
    //                    geojsonlayers.features[k].properties.color = layers[i].color
    //                }
    //
    //            }
    //        }
    //
    //    }
    //}
    //if (message != '') {
    //    var messageToDisplay = "CSS info missing for this layers: \n" + message
    //    alert(messageToDisplay)
    //}
    var color="#0000ff";
    createlayersCSS(layers[i].slug, color);
}

//Populate map's layers

var mapLayersNodes = loadLayers(layers);
var mapLayersArea = loadLayersArea(geojsonlayers);
//Map Controls
var baseMaps = {
    "OpenStreetMap": osmLayer,
        "Google Sat": googleSat,
        "Google Map": googleMap,
        "Google Hybrid": googleHybrid

};
var mapControl = L.control.layers(baseMaps, overlaymaps).addTo(map);

//Populate a select field wit Layers
getLayerListSlug(layers);
//console.log("markerMap:"+markerMap)
//console.log(markerMap)
function createlayersCSS(slug, color) {
    var cssClass = '.' + slug
    $("<style type='text/css'> " + cssClass + "{\
  background-color:" + color + ";\
    width: 30px;\
    height: 30px;\
    margin-left: 5px;\
    margin-top: 5px;\
    padding: 2px;\
    text-align: center;\
    vertical-align: middle;\
    font: 14px \"Helvetica Neue\", Arial, Helvetica, sans-serif;\
    border-radius: 20px;\
    border: thin solid;\
    border-color: black;\
    border-size: 3px;\
    line-height: 30px;\
    font-weight: bold;\
  } </style>").appendTo("head");
}

