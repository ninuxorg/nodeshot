//Marker manual insert on map
var markerToRemove
function onMapClick(e) {
	//alert(e.latlng);
	if (markerToRemove) {
		map.removeLayer(markerToRemove);
	}
	
	markerLocation = e.latlng
	markerLocationtoString = e.latlng.toString();
	marker = new L.Marker(markerLocation);
	markerToRemove=marker
	var popupelem= document.createElement('div');
	popupelem.innerHTML+='Is position correct ?<br>';
	popupelem.innerHTML+='<a class=\'confirm_marker\' onclick=markerConfirm(markerLocationtoString)>Confirm</a>&nbsp;';
	popupelem.innerHTML+='<a class=\'remove_marker\' onclick=markerDelete(marker)>Delete</a>';
	
	map
		
		.addLayer(marker);
	popup
		.setLatLng(e.latlng)
		.setContent(popupelem)
		.openOn(map);
	
}

//Marker delete
function markerDelete(marker) {
	map.removeLayer(marker);
	map.closePopup();	
}

//Marker confirm
function markerConfirm(marker) {
	openInsertDiv(marker);
	map.closePopup();
}

//function to catch and display PoI coordinates
function openInsertDiv(latlng){
	$("#valori").html('');
	//alert(latlng);
	var arrayLatLng=latlng.split(",");
	var lat=arrayLatLng[0].slice(7);
	var lng=arrayLatLng[1].slice(0,-1);
//	var address=   getData('http://nominatim.openstreetmap.org/reverse?format=json&lat='+lat+'&lon='+lng+'&zoom=18&addressdetails=1');
	//console.log(address);
	$("#node_insert").show();
	$("#lat").html(lat);
	$("#lng").html(lng);
	$("#address").html(address.display_name);
	
        }
//
//

function getLayerList(layers) {
	layerList=[];
	for(var i=0;i<layers.length;i++){
		layerList[i]={}
		var obj = layers[i];
		for(var key in obj){
			var attrName = key;
			var attrValue = obj[key];
			if (key=='slug' || key== 'name' ) {
				layerList[i][key]=attrValue;
			}	    
		}
	}
	var options = $("#Layer_select");	
	$.each(layerList, function(obj,city) {
		options.append($("<option />").val(city.slug).text(city.name));
		});
}

//Layers load
function loadLayers(layers) {
	var allLayers= []
	for (i in layers)
		{
		
		//alert(layers[i].name );
		var newCluster = new L.MarkerClusterGroup();
		var newClusterNodes=   getData('http://localhost:8000/api/v1/layers/'+layers[i].slug+'/geojson/');
		var newClusterLayer=loadNodes(newClusterNodes)	;
		newCluster.addLayer(newClusterLayer);
		map.addLayer(newCluster);
		var newClusterKey=layers[i].name;
		overlaymaps[newClusterKey]=newCluster;
		allLayers[i]=newCluster;
		}
	return allLayers;

}


function clearLayers()  {
            for (x in mapLayers) {
		//alert (x);
		mapLayers[x].clearLayers();
	    }
        }
	
//Load layer nodes

function loadNodes(newClusterNodes){

	var layer=
	L.geoJson(newClusterNodes, {
	onEachFeature: function (feature, layer)
		{
		//console.log(layer);
		slug=feature.properties.slug
		//alert(slug);
		node=   getData('http://localhost:8000/api/v1/nodes/'+slug+'/participation/');
		//console.log(node)
		var domelem = document.createElement('div');
		domelem.innerHTML ='<b>'+ node.name+'</b><br>';
		domelem.innerHTML += '<br> '+ feature.properties.address+'<br>';
		domelem.innerHTML += '<br> <b>Ratings average: </b>'+ node.participation.rating_count+'<br>';
		domelem.innerHTML += '<br> <b>Ratings count: </b>'+ node.participation.rating_count+'<br>';
		domelem.innerHTML += '<br> <b>Likes: </b>'+ node.participation.likes+'<br>';
		domelem.innerHTML += '<br> <b>Dislikes: </b>'+ node.participation.dislikes+'<br>';
		domelem.innerHTML += '<br> <b><a onclick=showComments(\''+node.slug+'\');>Comments: </b>'+ node.participation.comment_count+'</a><br>';
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
function showComments(node) {
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
