

//Map initialization
var map = L.map('map').setView([41.87, 12.49], 9);
var osm_layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
//var ggl_hybrid = new L.Google('HYBRID');
//var ggl_map = new L.Google('ROADMAP');
//var ggl_sat = new L.Google();
//OSM layer added to map
osm_layer.addTo(map);
map.on('click', onMapClick);
var popup = L.popup();
//Layer insert
var roma = new L.MarkerClusterGroup();
var pisa = new L.MarkerClusterGroup();
rome_nodes=   getData('http://localhost:8000/api/v1/layers/rome/geojson/');
pisa_nodes=   getData('http://localhost:8000/api/v1/layers/pisa/geojson/');
//console.log(hotspots)   ;
rome_nodes_layer=load_nodes(rome_nodes)	;
pisa_nodes_layer=load_nodes(pisa_nodes)	;

roma.addLayer(rome_nodes_layer);
pisa.addLayer(pisa_nodes_layer);
//Layer control creation
map.addLayer(roma);
map.addLayer(pisa); 
		 
var baseMaps = {
		"OpenStreetMap": osm_layer,
		//"Google Sat": ggl_sat,
		//"Google Map": ggl_map,
		//"Google Hybrid": ggl_hybrid
		
				};
				
var overlaymaps = {
			
			
			"Roma": roma,
			"Pisa" : pisa,
		};
L.control.layers(null,overlaymaps).addTo(map);


