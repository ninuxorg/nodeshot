var csrftoken = $.getCookie('csrftoken');
var markerToRemove //If users insert a new marker previous one has to be deleted from map
var nodeRatingAVG // Rating data has to be globally available for rating plugin to correctly work
var markerMap = {} //Object holding all nodes'id and a reference to their marker
var markerStatusMap = {}
var mapClusters = {}


/*
Colors are dinamically added to layers whe these are loaded.
If more than 8 layers need to be represented add more colors to the array.
*/

var colors = [
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
var status_colors = {
    'open': '#FF0000',
    'closed': '#00FF00'
}

//Map initialization
var map = L.map('map').setView([41.87, 12.49], 8);
var legend = L.control({position: 'bottomleft'});

//function removeStatusMarkers(status){
//    //event.stopPropagation();
//    for (var i in window.layers) {
//        var layer_slug = window.layers[i].slug
//        console.log(window.mapClusters[layer_slug])
//        console.log(window.markerStatusMap[layer_slug][status])
//        window.mapClusters[layer_slug].removeLayers(window.markerStatusMap[layer_slug][status])
//
//       //console.log(window.markerStatusMap[layer_slug][status])
//    }
//    L.DomEvent
//        //.addListener(toggleOpen, 'click', L.DomEvent.stopPropagation)
//        ////.addListener(toggleOpen, 'click', L.DomEvent.preventDefault)
//        //.addListener(toggleClosed, 'click', L.DomEvent.stopPropagation)
//        //.addListener(toggleClosed, 'click', L.DomEvent.preventDefault)
//        //.addListener(toggleOpen, 'click', function () { addStatusMarkers('open'); })
//        .removeListener(toggleOpen, 'click', function () { removeStatusMarkers('open'); })
//        //$(toggleOpenDiv).off()
//}
//
//function addStatusMarkers(status){
//    //event.stopPropagation();
//    for (var i in window.layers) {
//        var layer_slug = window.layers[i].slug
//        console.log(window.mapClusters[layer_slug])
//        console.log(window.markerStatusMap[layer_slug][status])
//        window.mapClusters[layer_slug].addLayers(window.markerStatusMap[layer_slug][status])
//
//       //console.log(window.markerStatusMap[layer_slug][status])
//    }
    //L.DomEvent
    //    
    //    .addListener(toggleOpen, 'click', function () { removeStatusMarkers('open'); })
    //    .removeListener(toggleOpen, 'click', function () { addStatusMarkers('open'); })
//}

legend.onAdd = function (map) {
    var div = L.DomUtil.create('div','mapLegend')
    div.innerHTML="<div><strong>Legend</strong>"
    _.each(status_colors,function(value, key, list){
        div.innerHTML += "<div style='clear:both;min-height:10px;width:100px;'>"
        div.innerHTML += "<div class='circle' style='float:left;background-color:"+value+"'></div>"
        div.innerHTML += "<div style='padding-left:10px;margin-top:-4px;float:left;'>"+key+" requests"+"</div>"
        div.innerHTML += "</div>"
        })
    div.innerHTML += "</div>"
    //var toggleOpenDiv = L.DomUtil.create('toggleOpen','',div)
    //var toggleClosedDiv = L.DomUtil.create('toggleClosed','',div)
    //toggleOpenDiv.innerHTML = " <span style='color:"+open_color+"'>Open requests</span><br>"
    //toggleOpenDiv.innerHTML += "<span style='color:"+closed_color+"'>Closed requests</span><br>"

    
    //toggleOpenDiv.innerHTML = "<input type='checkbox' id='toggleOpen' checked> <span style='color:"+open_color+"'>Open requests</span><br>"
    //toggleOpenDiv.innerHTML += "<input type='checkbox' id='toggleClosed'> <span style='color:"+closed_color+"'>Closed requests</span><br>"
    ////$(toggleOpenDiv).on('click',function(){removeStatusMarkers('open');})
    //
    //L.DomEvent
    //    .addListener(toggleOpenDiv, 'click', L.DomEvent.stopPropagation)
    //    //.addListener(toggleOpen, 'click', L.DomEvent.preventDefault)
    //    //.addListener(toggleClosed, 'click', L.DomEvent.stopPropagation)
    //    //.addListener(toggleClosed, 'click', L.DomEvent.preventDefault)
    //    .addListener(toggleOpenDiv, 'click', function () { removeStatusMarkers('open'); })
    //    //.addListener(toggleOpenDiv, 'click', function () { test(); });
    //
    return div;
};



legend.addTo(map);
var mapBoxLayer = new L.tileLayer('//a.tiles.mapbox.com/v3/nemesisdesign.hcj0ha2h/{z}/{x}/{y}.png').addTo(map);
var osmLayer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
//Uncomment for Google maps. Must be checked if it works in IE
var googleHybrid = new L.Google('HYBRID');
var googleMap = new L.Google('ROADMAP');
var googleSat = new L.Google();

//OSM layer added to map
mapBoxLayer.addTo(map);
map.on('click', onMapClick);
var popup = L.popup();

//Layer insert on map
var overlaymaps = {};


//Load data from server
var layers = getData(window.__BASEURL__ + 'layers/'); //layers
var geojsonlayers = getData(window.__BASEURL__ + 'layers.geojson'); //layers' area


for (var i in layers) {
    createlayersCSS(layers[i].slug, colors[i]);
}

//Populate map's layers

var mapLayersNodes = loadLayers(layers);
//var mapLayersArea = loadLayersArea(geojsonlayers);
//Map Controls
var baseMaps = {
    "MapBox": mapBoxLayer,
    "OpenStreetMap": osmLayer,
    "Google Sat": googleSat,
    "Google Map": googleMap,
    "Google Hybrid": googleHybrid

};
var mapControl = L.control.layers(baseMaps, overlaymaps).addTo(map);

//Populate a select field with Layers
getLayerListSlug(layers);

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

