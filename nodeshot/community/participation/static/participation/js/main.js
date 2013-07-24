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
var layers= getData('http://localhost:8000/api/v1/layers/');
//console.log(layers)
var mapLayers=loadLayers(layers);
//var layerList=getLayerList(layers);
//console.log(layerList);
var baseMaps = {
		"OpenStreetMap": osmLayer,
		//Uncomment for Google maps. Works only in quirk mode.
		"Google Sat": googleSat,
		"Google Map": googleMap,
		"Google Hybrid": googleHybrid
		
				};
L.control.layers(baseMaps,overlaymaps).addTo(map);
//showLayerProperties()




