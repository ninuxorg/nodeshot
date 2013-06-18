//function to catch and display PoI coordinates
		function open_insert(latlng)
		{
			//alert(latlng);
			var arr_latlng=latlng.split(",");
			var lat=arr_latlng[0].slice(7);
			var lng=arr_latlng[1].slice(0,-1);
			str_latlng="Latitudine:" + lat + "<br>Longitudine:" + lng
		//	 var address=   eval ("(" + getData('http://nominatim.openstreetmap.org/reverse?format=json&lat='+lat+'&lon='+lng+'&zoom=18&addressdetails=1' + ")"));
			var address=   getData('http://nominatim.openstreetmap.org/reverse?format=json&lat='+lat+'&lon='+lng+'&zoom=18&addressdetails=1');
		//	alert (address);
		//	console.log(address);
			var address_display=address.display_name;
		//	alert(address_display);
			$("#lat").html(lat);
			$("#lng").html(lng);
			$("#address").html(address.display_name);
		}
 //Layer insert
     
    	function onMapClick(e) {
			//alert(e.latlng);
			var markerLocation = e.latlng
			var marker = new L.Marker(markerLocation);
			map
				.addLayer(marker);
			popup
				.setLatLng(e.latlng)
				.setContent("Inserisci un commento e invia il PoI")
				.openOn(map);
			open_insert(e.latlng.toString());
		}
//Load layer nodes
	
	function load_nodes(geojson_layer_nodes)		
	L.geoJson(geojson_layer_nodes, {
	onEachFeature: function (feature, layer) {
	//layer.bindPopup("<br><button onclick=\"alert('"+feature.properties.name+"')\";>Apri box commenti</button>");
	//layer.bindPopup(feature.properties.popupContent+"<br><button onclick=\"alert('Il resto alla prossima puntata')\";>Apri box commenti</button>");
	
	slug=feature.properties.slug
	//alert(slug);
	node=   getData('http://localhost:8000/api/v1/nodes/'+slug+'/participation/');
	console.log(node)
	//node_obj=JSON.parse(node);
	
	var domelem = document.createElement('div');
	domelem.href = "#";
	domelem.innerHTML = node.name+'<br>';
	domelem.innerHTML += '<br> '+ feature.properties.address+'<br>';
	domelem.innerHTML += '<br> <b>Ratings average: </b>'+ node.participation.rating_count+'<br>';
	domelem.innerHTML += '<br> <b>Ratings count: </b>'+ node.participation.rating_count+'<br>';
	domelem.innerHTML += '<br> <b>Comments: </b>'+ node.participation.comment_count+'<br>';
	domelem.innerHTML += '<br> <b>Likes: </b>'+ node.participation.likes+'<br>';
	domelem.innerHTML += '<br> <b>Dislikes: </b>'+ node.participation.dislikes+'<br>';

	domelem.onclick = function() {
	    alert(this.href); 
	    // do whatever else you want to do 
	};
	layer.bindPopup(domelem);
	}
	});
//Ajax check
    
  $(function() {
    $.ajaxSetup({
        error: function(jqXHR, exception) {
            if (jqXHR.status === 0) {
                alert('Not connect.\n Verify Network.');
            } else if (jqXHR.status == 404) {
                alert('Requested page not found. [404]');
            } else if (jqXHR.status == 500) {
                alert('Internal Server Error [500].');
            } else if (exception === 'parsererror') {
                alert('Requested JSON parse failed.');
            } else if (exception === 'timeout') {
                alert('Time out error.');
            } else if (exception === 'abort') {
                alert('Ajax request aborted.');
            } else {
                alert('Uncaught Error.\n' + jqXHR.responseText);
            }
        }
    });
});
  
 //Get Data
 

function getData(url) {
var data;
    $.ajax({
        async: false, //thats the trick
        url: url,
        dataType: 'json',
        success: function(response){
           data = response;
        }
        
    });
    //alert(data);
    return data;
}

// Load #loading layers
// Assuming that the div or any other HTML element has the ID = loading and it contains the necessary loading image.

$('#loading').hide(); //initially hide the loading icon
 
        $('#loading').ajaxStart(function(){
            $(this).show();
            //console.log('shown');
        });
        $("#loading").ajaxStop(function(){
            $(this).hide();
            //  console.log('hidden');
        }); 
