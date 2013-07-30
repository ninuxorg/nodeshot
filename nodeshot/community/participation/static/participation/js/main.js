//Map initialization
var map = L.map('map').setView([41.87, 12.49], 9);
var osmLayer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
//Uncomment for Google maps. Works only in quirk mode.
var googleHybrid = new L.Google('HYBRID');
var googleMap = new L.Google('ROADMAP');
var googleSat = new L.Google();

//OSM layer added to map
osmLayer.addTo(map);
map.on('click', onMapClick);
var popup = L.popup();

//Layer insert on map
var overlaymaps={};
var layers= getData(window.__BASEURL__+'api/v1/layers/');
console.log(layers)
var mapLayersArea=loadLayersArea(layers);
var mapLayers=loadLayers(layers);
var baseMaps = {
		"OpenStreetMap": osmLayer,
		//Uncomment for Google maps. Works only in quirk mode.
		"Google Sat": googleSat,
		"Google Map": googleMap,
		"Google Hybrid": googleHybrid
		
				};
var mapControl=L.control.layers(baseMaps,overlaymaps).addTo(map);
getLayerListSlug(layers,"selectLayerNodeList");

//for (var key in markerMap) {
//  console.log(markerMap[key].toGeoJSON());
//}


