NS_311.csrftoken = $.getCookie('csrftoken');
NS_311.markerToRemove //If users insert a new marker previous one has to be deleted from map
NS_311.nodeRatingAVG // Node Rating data has to be globally available for jquery-raty rating plugin to correctly work
NS_311.markerMap = {} //Object containing all requests'id and a reference to their marker
NS_311.markerStatusMap = {"open": [], "closed": []} //Object containing arrays of open and closed requests and a reference to their marker
NS_311.mapClusters = {} // Object containing layers as leaflet Clusters


/*
Colors are dinamically added to layers whe these are loaded.
If more than 8 layers need to be represented add more colors to the array.
*/

NS_311.colors = [
    '#0000ff',
    '#DFA171',
    '#CBC7B6',
    '#FED508',
    '#610B5E',
    '#292323',
    '#FF8000',
    '#FFFF00',
    
]

/*
 Status colors are green(open) and red ( closed).
 Don't use these colors to style layers.
 */
NS_311.status_colors = {
    'open': '#FF0000',
    'closed': '#00FF00'
}

//Map initialization
var map = L.map('map').setView([41.87, 12.49], 8);
var legend = L.control({position: 'bottomleft'});
var osmLayer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
//var mapBoxLayer = new L.tileLayer(NS_311.TILESERVER_URL)
var googleHybrid = new L.Google('HYBRID');
var googleMap = new L.Google('ROADMAP');
var googleSat = new L.Google();

//OSM layer added to map
//mapBoxLayer.addTo(map);
map.on('click', onMapClick);
var popup = L.popup();

//Layer insert on map
var overlaymaps = {};

//Load data from server
var layers = getData(window.__BASEURL__ + 'layers/'); //layers
//var geojsonlayers = getData(window.__BASEURL__ + 'layers.geojson'); //layers' area

for (var i in layers) {
    createlayersCSS(layers[i].slug, NS_311.colors[i]);
}

//Populate map's layers

var mapLayersNodes = loadLayers(layers);

//Map Controls
var baseMaps = {
    "OpenStreetMap": osmLayer,
 //   "MapBox": mapBoxLayer,
    "Google Sat": googleSat,
    "Google Map": googleMap,
    "Google Hybrid": googleHybrid

};
//var mapControl = L.control.layers(baseMaps, overlaymaps).addTo(map);
legend.onAdd = function (map) {
    var mapLegend = L.DomUtil.create('div','mapLegend')
    mapLegend.innerHTML="<div><strong>Legend</strong>"
    _.each(NS_311.status_colors,function(value, key, list){
        mapLegend.innerHTML += "<div style='clear:both;min-height:10px;width:100px;'>"
        mapLegend.innerHTML += "<div class='circle' style='float:left;background-color:"+value+"'></div>"
        mapLegend.innerHTML += "<div style='padding-left:10px;margin-top:-4px;float:left;'>"+key+" requests <strong>("+ NS_311.markerStatusMap[key].length + ")</strong></div>"
        mapLegend.innerHTML += "</div>"
        })
    mapLegend.innerHTML += "</div>"
    return mapLegend;
};
legend.addTo(map);

var mapControl = L.control.layers(baseMaps, overlaymaps).addTo(map);
//Populate a select field with Layers
getLayerListSlug(layers);





function createlayersCSS(slug, color) {
    var cssClass = '.' + slug
    $("<style type='text/css'> " + cssClass + "{\
    background-color:" + color + ";\
    width: 50px;\
    height: 50px;\
    margin-left: 5px;\
    margin-top: 5px;\
    padding: 2px;\
    text-align: center;\
    vertical-align: middle;\
    font: 14px \"Helvetica Neue\", Arial, Helvetica, sans-serif;\
    border-radius: 20px;\
    border: thin solid;\
    border-color: black;\
    border-size: 5px;\
    line-height: 25px;\
    font-weight: bold;\
  } </style>").appendTo("head");
}

