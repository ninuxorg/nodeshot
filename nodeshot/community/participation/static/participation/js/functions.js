//Marker manual insert on map

function onMapClick(e) {
	//alert(e.latlng);
	if (marker_to_remove) {
		map.removeLayer(marker_to_remove);
	}
	
	markerLocation = e.latlng
	markerLocationtoString = e.latlng.toString();
	var popupelem= document.createElement('div');
	marker = new L.Marker(markerLocation);
	marker_to_remove=marker
	//popupelem.innerHTML=markerLocation;
	popupelem.innerHTML+='Is position correct ?<br>';
	popupelem.innerHTML+='<a class=\'confirm_marker\' onclick=marker_confirm(markerLocationtoString)>Confirm</a>&nbsp;';
	popupelem.innerHTML+='<a class=\'remove_marker\' onclick=marker_delete(marker)>Delete</a>';
	
	map
		
		.addLayer(marker);
	popup
		.setLatLng(e.latlng)
		.setContent(popupelem)
		.openOn(map);
	
}

//Marker delete
function marker_delete(marker) {
	map.removeLayer(marker);
	map.closePopup();	
}

//Marker confirm
function marker_confirm(marker) {
	open_insert(marker);
	map.closePopup();
}

//function to catch and display PoI coordinates
function open_insert(latlng){
	$("#valori").html('');
	//alert(latlng);
	var arr_latlng=latlng.split(",");
	var lat=arr_latlng[0].slice(7);
	var lng=arr_latlng[1].slice(0,-1);
	var str_latlng="Latitudine:" + lat + "<br>Longitudine:" + lng
	// var address=   eval ("(" + getData('http://nominatim.openstreetmap.org/reverse?format=json&lat='+lat+'&lon='+lng+'&zoom=18&addressdetails=1' + ")"));
	var address=   getData('http://nominatim.openstreetmap.org/reverse?format=json&lat='+lat+'&lon='+lng+'&zoom=18&addressdetails=1');
	//console.log(address);
	//alert(address_display);
	$("#node_insert").show();
	$("#lat").html(lat);
	$("#lng").html(lng);
	$("#address").html(address.display_name);
	var options = $("#Layer_select");	
  }  
//    //don't forget error handling!
   $.each(layer_slug, function(item) {
      options.append($("<option />").val(item.name).text(item.name));
  });
//
//

function get_layer_slug(layers) {
	var layer_slug={};
	for(var i=0;i<layers.length;i++){
		var obj = layers[i];
		for(var key in obj){
		
		 //var attrName = key;
		 var attrValue = obj[key];
		if (key=='slug' ) {
			var attrValue = obj[key];
			//alert (attrName);
			//alert (attrValue);
			test=key;
			layer_slug[i]=obj[key];
		}
	    
    }
}
return layer_slug;
}

//Layers load
function load_layers(layers) {
	var AllLayers= []
	for (i in layers)
		{
		
		//alert(layers[i].name );
		var newCluster = new L.MarkerClusterGroup();
		var newCluster_nodes=   getData('http://localhost:8000/api/v1/layers/'+layers[i].slug+'/geojson/');
		var newCluster_layer=load_nodes(newCluster_nodes)	;
		newCluster.addLayer(newCluster_layer);
		map.addLayer(newCluster);
		var newClusterKey=layers[i].name;
		overlaymaps[newClusterKey]=newCluster;
		AllLayers[i]=newCluster;
		//console.log(AllLayers[i])
		}
	return AllLayers;

}


function clear_layers(layer_group)  {
            for (x in layer_group) {
		//alert (x);
		layer_group[x].clearLayers();
	    }
        }
	
//Load layer nodes

function load_nodes(geojson_layer_nodes){

	layer=
	L.geoJson(geojson_layer_nodes, {
	onEachFeature: function (feature, layer)
		{
		//console.log(layer);
		slug=feature.properties.slug
		//alert(slug);
		node=   getData('http://localhost:8000/api/v1/nodes/'+slug+'/participation/');
		console.log(node)
		//node_obj=JSON.parse(node);
		var domelem = document.createElement('div');
		domelem.innerHTML ='<b>'+ node.name+'</b><br>';
		domelem.innerHTML += '<br> '+ feature.properties.address+'<br>';
		domelem.innerHTML += '<br> <b>Ratings average: </b>'+ node.participation.rating_count+'<br>';
		domelem.innerHTML += '<br> <b>Ratings count: </b>'+ node.participation.rating_count+'<br>';
		domelemhttps://mail.google.com/mail/u/0/?shva=1#inbox.innerHTML += '<br> <b>Likes: </b>'+ node.participation.likes+'<br>';
		domelem.innerHTML += '<br> <b>Dislikes: </b>'+ node.participation.dislikes+'<br>';
		domelem.innerHTML += '<br> <b><a onclick=show_comments(\''+node.slug+'\');>Comments: </b>'+ node.participation.comment_count+'</a><br>';
		//console.log(layer.options);
		layer.bindPopup(domelem);
		}
		
	});
	return layer;	
}
	
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

//Show_comments
function show_comments(node) {
	var html_text=node+'<br>&nbsp;'
	//$("#valori").html('');
	url='http://localhost:8000/api/v1/nodes/'+node+'/comments/?format=json';
	comments=   getData(url);
	console.log(comments);
	for (var i = 0; i < comments.length; i++) { 

		html_text+='<div class=\'comment_text\'>';	
		//html_text+='<li>Added:'+comments[i].added+'</li>';
		html_text+=comments[i].text;
		html_text+='</div>';
		html_text+='<div class=\'comment_user\'>';	
		html_text+='Posted by: '+comments[i].username+' on ';
		html_text+=comments[i].added+'<br>';
		html_text+='</div>';
		}
	//alert(html_text);
	html_text+='Add your:<br>';
	$("#node_insert").hide();
	$("#valori").html(html_text);

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
