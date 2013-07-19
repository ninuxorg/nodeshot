//Marker manual insert on map
//var nodeDiv = $("#nodeDiv");
var markerToRemove
var csrftoken = $.cookie('csrftoken');
//console.log(csrftoken)
var nodeSlug
var comment


$(document).ready(function(){
    $('html').bind('click', function (event) {
	//alert (event.pageX);

    });
});

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
//Create a list with layers' slug and name
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
		var newCluster = new L.MarkerClusterGroup(
		//					  {
		//iconCreateFunction: function (cluster) {
		//		return L.divIcon({
		//			html: cluster.getChildCount(),
		//			className: layers[i].slug,
		//			iconSize: L.point(40, 40) });
		//			},
		//zoomToBoundsOnClick: false
		//	}
			);
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

//Delete all layers from map
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
	onEachFeature: function (feature, layer) {
		//nodeSlug=feature.properties.slug;
		nodeAddress=feature.properties.address;
		layer.on('click', function (e) {
			populateNodeDiv(feature.properties.slug);
			this.bindPopup(nodeDiv)
			
				});
		//console.log(nodeSlug);
		}
		
	});
	return layer;	
}

////Create div that will display nodes'info
function createNodeDiv(nodeSlug) {
		nodeDiv = document.createElement('div');
		nodeDiv.id=nodeSlug;
		populateNodeDiv (nodeSlug);
//
}

function populateNodeDiv(nodeSlug) {
	
	nodeDiv = document.createElement('div');
	nodeDiv.id=nodeSlug;
	node=   getData('http://localhost:8000/api/v1/nodes/'+nodeSlug+'/participation/');
	nodeName=node.name;
	nodeRatingCount=node.participation.rating_count;
	nodeRatingAVG=node.participation.rating_avg;
	nodeLikes=node.participation.likes;
	nodeDislikes=node.participation.dislikes;
	nodeVoteCount=nodeLikes+nodeDislikes;
	nodeComments=node.participation.comment_count;
	//alert(node.name)
	$(nodeDiv).append('<b>'+nodeName+'</b><br>');
	if (nodeRatingCount==0) {
		$(nodeDiv).append('Not rated yet<br>');
	}
	else {
	$(nodeDiv).append('Rated:'+node.participation.rating_avg+'<br> by '+node.participation.rating_count+' people<br>');
	}
	
	if (nodeVoteCount==0) {
		$(nodeDiv).append('Not voted yet</br>');
	}
	else {
	$(nodeDiv).append('Likes to:'+nodeLikes+' people.<br>');
	$(nodeDiv).append('Don\'t likes to:'+nodeDislikes+' people.<br>');
	}
	
	if (nodeComments==0) {
		$(nodeDiv).append('Not commented yet<br>');
	}
	else {
		$(nodeDiv).append('<a onclick=showComments("'+nodeSlug+'");>Comments: '+ node.participation.comment_count+'</a><br>');

	}

	return(nodeDiv)

}

function updateNodeDiv(nodeSlug) {
	
	node=   getData('http://localhost:8000/api/v1/nodes/'+nodeSlug+'/participation/');
	nodeName=node.name;
	nodeRatingCount=node.participation.rating_count;
	nodeRatingAVG=node.participation.rating_avg;
	nodeLikes=node.participation.likes;
	nodeDislikes=node.participation.dislikes;
	nodeVoteCount=nodeLikes+nodeDislikes;
	nodeComments=node.participation.comment_count;
	//alert(node.name)
	$(nodeDiv).append('<b>'+nodeName+'</b><br>');
	if (nodeRatingCount==0) {
		$(nodeDiv).append('Not rated yet<br>');
	}
	else {
	$(nodeDiv).append('Rated:'+node.participation.rating_avg+'<br> by '+node.participation.rating_count+' people<br>');
	}
	
	if (nodeVoteCount==0) {
		$(nodeDiv).append('Not voted yet</br>');
	}
	else {
	$(nodeDiv).append('Likes to:'+nodeLikes+' people.<br>');
	$(nodeDiv).append('Don\'t likes to:'+nodeDislikes+' people.<br>');
	}
	
	if (nodeComments==0) {
		$(nodeDiv).append('Not commented yet<br>');
	}
	else {
		$(nodeDiv).append('<a onclick=showComments("'+nodeSlug+'");>Comments: '+ node.participation.comment_count+'</a><br>');

	}

	return(nodeDiv)

}

//Show_comments
function showComments(nodeSlug) {
	//alert(JSON.stringify(nodeSlug))
	//$("#valori").html('');
	var node=nodeSlug
	url='http://localhost:8000/api/v1/nodes/'+node+'/comments/?format=json';
	comments=   getData(url);
	//console.log(comments);
	htmlText='<b>'+node+'</b><br>';
	for (var i = 0; i < comments.length; i++) { 

		htmlText+='<div class=\'comment_text\'>';	
		//htmlText+='<li>Added:'+comments[i].added+'</li>';
		htmlText+=comments[i].text;
		htmlText+='</div>';
		htmlText+='<div class=\'comment_user\'>';	
		htmlText+='Posted by: '+comments[i].username+' on ';
		htmlText+=comments[i].added+'<br>';
		htmlText+='</div>';
		}
	//alert(htmlText);
	htmlText+='Add your:<br>';
	htmlText+='<textarea id="commentText"></textarea><br>';
	//htmlText+='<button onclick=alert(\'commento\')>Add</button>'
	var comment="Altro ciao"
	htmlText+='<button onclick=postComment("'+node+'");>Add</button>'
	$("#node_insert").hide();
	$("#valori").html(htmlText);

}



function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}


//Ajax check
    
 $(function() {
	
    $.ajaxSetup({
	beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    },
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
  
 //Get Data in async way, so that it can return an object to a variable
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


//post a comment
function postComment(nodeSlug) {
//nodeSlug='fusolab';
//alert (nodeSlug);
comment=$("#commentText").val();
    $.ajax({
        type: "POST",
        url: 'http://localhost:8000/api/v1/nodes/'+nodeSlug+'/comments/',
	data: { "text": comment},
        dataType: 'json',
        success: function(response){	
	var nodeDiv=  $("#" + nodeSlug);
	$(nodeDiv).html('')
        updateNodeDiv (nodeSlug);
        }
        
    });
}

//post data to API
function login() {
user=$("#user").val();
var password=$("#password").val();
    $.ajax({
        type: "POST",
        url: "http://localhost:8000/api/v1/account/login/",
	data: { "username": user, "password": password },
        dataType: 'json',
        success: function(response){
        showLogout(user);
        }
    });
}

function logout() {
    $.ajax({
        type: "POST",
        url: "http://localhost:8000/api/v1/account/logout/",
        dataType: 'json',
        success: function(response){
	showLogin();
        }
        
    });
}

function showLogin() {
	$('#userForm').html('');
	var login_html='<input id="user" class="span2" type="text" placeholder="Email">'
	login_html+='<input id="password" class="span2" type="password"placeholder="Password">'
        login_html+=' <button id="loginButton" type="button" onclick=login() class="btn">Sign in</button>'
	$('#userForm').append(login_html)
}

function showLogout(user) {
	$('#userForm').html('');
	var logout_html='<font color="#FFFFFF">Hi ' + user + ' </font>'
	logout_html+='<button id="logoutButton" type="button" onclick=logout() class="btn">Sign out</button>'
	$('#userForm').append(logout_html)
	
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
