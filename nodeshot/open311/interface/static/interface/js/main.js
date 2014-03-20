var csrftoken = $.getCookie('csrftoken');
var markerToRemove //If users insert a new marker previous one has to be deleted from map
var nodeRatingAVG // Rating data has to be globally available for rating plugin to correctly work
var markerMap = {} //Object holding all nodes'id and a reference to their marker
var markerStatusMap = {}
var mapClusters = {}
//Map initialization
var colors = [//if more than 4 layers need to be represented add more colors to the array
    '#0000ff',
    '#FF8000',
    '#610B5E',
    '#FFFF00',
    
]
var status_colors = {
    'open': '#FF0000',
    'closed': '#00FF00'
}
var map = L.map('map').setView([41.87, 12.49], 8);
var legend = L.control({position: 'bottomleft'});

function test()  {
    
    alert('test');
    //return false;
}

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
    //open_color = statuses.open.fill_color;
    //closed_color = statuses.closed.fill_color;
    var div = L.DomUtil.create('div','mapLegend')
    div.innerHTML="<strong>Legend</strong><br>"
    _.each(status_colors,function(value, key, list){
        console.log(key+value)
        var subDiv = L.DomUtil.create(key,'',div)
        subDiv.innerHTML = " <span style='color:"+value+"'>"+key+"</span><br>"
        
        })
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
    createlayersCSS(layers[i].slug, colors[i]);
}

//Populate map's layers

var mapLayersNodes = loadLayers(layers);
//var mapLayersArea = loadLayersArea(geojsonlayers);
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

