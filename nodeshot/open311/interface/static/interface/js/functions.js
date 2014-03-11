/* LAYERS LIST CREATION
 * ====================*/

//Create a list with layers' slug and name
    function getLayerListSlug(layers) {
        var tmplMarkup = $('#tmplLayerList').html();
        $.each(layers, function (key, value) {
            var layer = {};
            layer = value;
            var compiledTmpl = _.template(tmplMarkup, {
                layer: layer
            });
            $('#selectLayer').append(compiledTmpl);
        });
    }

    /* CREATE AND SHOW NODE LIST
     * =========================*/

    function createNodeList() {
        var layer = $("#selectLayer").val();
        if (layer != " ") {
            $.ajax({
                type: 'GET',
                url: window.__BASEURL__ + 'api/v1/open311/requests?service_code=node&layer=' + layer ,
                dataType: 'json',
                contentType: 'application/json; charset=utf-8',
                success: function (result) {
                    //alert('success')
                    addToList(result)
                },
            })
        }
    }

    function addToList(data) {
        //alert('test')
        console.log(data)
        $("#valori").html('');
        $("#nodelist").html('');
        var nodes = data;
        var tmplMarkup = $('#tmplNodelist').html();
        var compiledTmpl = _.template(tmplMarkup, {
            nodes: nodes
        });
        $("#nodelist").append(compiledTmpl);

        $('a.list-link').click(function (e) {
            var slug = $(this).data('id');
            var marker = markerMap[slug];
            populateOpen311Div(slug,"true");
            marker.addTo(map)
            marker.bindPopup(nodeDiv)
            //populateRating(slug,nodeDiv,nodeRatingAVG)
            marker.openPopup()
        })
    }

    /* INSERTION OF NODES ON MAP ON PAGE LOAD
     * ====================================== */

    //function style(feature) {
    //    var color = feature.properties.color;
    //    return {
    //        weight: 1,
    //        opacity: 1,
    //        color: 'black',
    //        clickable: false,
    //        dashArray: '3',
    //        fillOpacity: 0.2,
    //        fillColor: color
    //    };
    //}

    function loadLayersArea(layers) {
        /*
         * Puts layer areas on map
         */
        var allLayersArea = []
        for (var i in layers.features) {

            var newArea = L.geoJson(layers.features[i], {
                style: {
            weight: 1,
            opacity: 1,
            color: 'black',
            clickable: false,
            dashArray: '3',
            fillOpacity: 0.2,
            fillColor: layers.features[i].properties.color
        }
            }).addTo(map);
            var newAreaKey = "<span style='font-weight:bold;color:" + layers.features[i].properties.color + "'>" + layers.features[i].properties.name + " Area</span>";
            overlaymaps[newAreaKey] = newArea;
            allLayersArea[i] = newArea;
        }
        return allLayersArea;
    }

    function loadLayers(layers) {
        /*
         * Takes all node of a layer and puts them on map in a Leaflet Clustered group
         */
        var allLayers = []
        for (var i in layers) {
            var color = layers[i].color;
            var clusterClass = layers[i].slug; //CSS class with same name of the layer
            //Creates a Leaflet cluster group styled with layer's colour
            window.mapClusters[layers[i].slug] = createCluster(clusterClass);
            window.markerStatusMap[layers[i].slug]={"open":[],"closed":[]}
            //var newCluster = window.mapClusters[layers[i].slug];
            //Loads nodes in the cluster
            var newClusterNodes = getData(window.__BASEURL__ + 'api/v1/open311/requests?service_code=node&layer='+layers[i].slug );
            var GeoJSON= new geojsonColl();
                for (var n in newClusterNodes){
                            
                                    var feature = new featureConstructor;
                                    feature.geometry.coordinates = [newClusterNodes[n].lng,
                                                                   newClusterNodes[n].lat]
                                    feature.properties = newClusterNodes[n]
                                    GeoJSON.features.push(feature)
                                        
    
                                }
            
            var newClusterLayer = loadNodes(layers[i].slug,GeoJSON, colors[i]);
            window.mapClusters[layers[i].slug].addLayer(newClusterLayer);
            //Adds cluster to map
            map.addLayer(window.mapClusters[layers[i].slug]);
            //Creates map controls for the layer
            var newClusterKey = "<span style='color:"+colors[i]+"'>" + layers[i].name + "</span>";
            overlaymaps[newClusterKey] = window.mapClusters[layers[i].slug];
            allLayers[i] = window.mapClusters[layers[i].slug];
        }
        return allLayers;

    }


    function createCluster(clusterClass) {
        /*
         * Creates cluster group
         */
        var newCluster = new L.MarkerClusterGroup({
            iconCreateFunction: function (cluster) {
                return L.divIcon({
                    html: cluster.getChildCount(),
                    className: clusterClass,
                    iconSize: L.point(30, 30)
                });
            },
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: true,
            zoomToBoundsOnClick: true
        });
        return newCluster;
    }


    function loadNodes(layer_slug,newClusterNodes, color) {
        /*
         * Load nodes in cluster group and defines click properties for the popup window
         */
        var layer = L.geoJson(newClusterNodes, {

            onEachFeature: function (feature, layer) {
                layer.on('click', function (e) {
                    console.log(feature)
                    populateOpen311Div(feature.properties.request_id, "true");
                    this.bindPopup(nodeDiv);
                    //populateRating(feature.id, nodeDiv, nodeRatingAVG)
                    //this.bindPopup(feature.properties.request_id)
                });

            },
            pointToLayer: function (feature, latlng) {
                var marker = new
                L.circleMarker(latlng, {
                    radius: 8,
                    fillColor: window.statuses[feature.properties.status].fill_color,
                    color: color,
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
                //console.log(feature.properties.name)
                window.markerMap[feature.properties.request_id] = marker;
                window.markerStatusMap[layer_slug][feature.properties.status].push(marker)

                return marker;
            }

        });

        return layer;
    }


    /* USER'S INSERTION OF NODES ON MAP 
     * ==================================== */

    function onMapClick(e) {
        /*
         *Creates marker object
         */
        if (markerToRemove) {
            map.removeLayer(markerToRemove);
        }

        markerLocation = e.latlng
        marker = new L.Marker(markerLocation);
        markerToRemove = marker
        var popupelem = document.createElement('div');
        popupelem.id = "insertMarker";
        var tmplMarkup = $('#tmplConfirmPos').html();
        var compiledTmpl = _.template(tmplMarkup);
        $(popupelem).html(compiledTmpl);

        map.addLayer(marker);
        popup.setLatLng(e.latlng)
            .setContent(popupelem)
            .openOn(map);

    }

    function markerDelete(marker) {
        /*
         * Deletes inserted marker from map
         */
        map.removeLayer(marker);
        map.closePopup();
    }

    function markerConfirm(marker) {
        /*
         * Opens node's insertion form
         */
        openForm(marker);
        map.closePopup();

    }

    
    function openForm(marker){
            var latlngToString = marker.toString();
            var arrayLatLng = latlngToString.split(",");
            var lat = arrayLatLng[0].slice(7);
            var lng = arrayLatLng[1].slice(0, -1);
            //console.log(nodeToInsert)
            var latlng = new L.LatLng(lat, lng);
            
            //console.log(layers)
            $('#overlay').fadeIn('fast',function(){
            $('#serviceRequestForm').show();
	    $('#serviceRequestForm').html('<a class="boxclose"  id="boxclose"></a>');
	    $('#boxclose').on("click",function(){
				       $('#serviceRequestForm').hide("fast",function(){
				       $('#overlay').fadeOut('fast');
				  });
		});
	    var tmplMarkup = $('#tmplInsertNode').html();
            var compiledTmpl = _.template(tmplMarkup,{layers:layers});
            var nodeInsertDiv = $("<div>", {
                id: "serviceRequestForm"
            });
    
            $('#serviceRequestForm').append(compiledTmpl);
            $("#requestLng").val(lng);
            $("#requestLat").val(lat);
            $('#requestLng').attr('readonly', true);
            $('#requestLat').attr('readonly', true);
            getAddress(lat,lng);
            $("#requestForm").submit(function(event){
 
            //disable the default form submission
            event.preventDefault();
            //grab all form data  
            var formData = new FormData($(this)[0]);
            var layer_inserted = $( this).serializeArray()[1]['value']
            //console.log( layer_inserted  );
 
            $.ajax({
              url: window.__BASEURL__ + 'api/v1/open311/requests/',
              type: 'POST',
              data: formData,
              async: false,
              cache: false,
              contentType: false,
              processData: false,
              success: function (returndata) {
                //console.log(returndata);
                //console.log( layer_inserted  );
                //clearLayers();
                    //map.removeControl(mapControl)
                    //mapLayersArea = loadLayersArea(geojsonlayers);
                    //mapLayersNodes = loadLayers(layers);
                    //mapControl = L.control.layers(baseMaps, overlaymaps).addTo(map);
                    newMarker = L.marker(latlng).addTo(map);
                    window.mapClusters[layer_inserted].addLayer(newMarker)
                    popupMessage="Request has been inserted<br>"
                    
                    var url = window.__BASEURL__ + 'open311/request/'
                    var requestUrl = url  + returndata
                    popupMessage+="<br><a href='"+requestUrl+"'>"+returndata+"</a>"

                    newMarker.bindPopup(popupMessage).openPopup();
                    map.panTo(latlng)
                    //newMarker.bindPopup(nodeDiv).openPopup();
                    $('#serviceRequestForm').hide("fast",function(){
				       $('#overlay').fadeOut('fast');})
              },
              error: function (jqXHR,error, errorThrown) {
                    console.log(jqXHR)
                    $("#request_messages").html(jqXHR.responseText);
                }
            });
 
  return false;
});
});
}
    


    function clearLayers() {
        /*
         * Delete all layers from map
         */
        for (var x in mapLayersNodes) {
            mapLayersNodes[x].clearLayers();
        }

        for (var y in mapLayersArea) {
            mapLayersArea[y].clearLayers();
        }
    }

    /* DISPLAYING OF NODES' PROPERTIES 
     * ================================ */
    function populateOpen311Div(nodeSlug, create) {
        /*
         * Populates a Div with node's participation data
         * 
         */

        if (create === "true") {
            nodeDiv = document.createElement('div');
            nodeDiv.id = nodeSlug;
        }
        
        var node = getData(window.__BASEURL__ + 'api/v1/open311/requests/' + nodeSlug);
        console.log(node)
        //var nodeName = node.name;
        var status = node.status;
        var nodeLayer = node.layer;
        var requestID = nodeSlug;
        var url = window.__BASEURL__ + 'open311/request/' + nodeSlug

        
        var tmplMarkup = $('#tmplOpen311Popup').html();
        var compiledTmpl = _.template(tmplMarkup, {
            request_id: requestID,
            status: status,
            url: url,
        });
        $(nodeDiv).append(compiledTmpl);

        

        return (nodeDiv, nodeRatingAVG)

    }

    function populateNodeDiv(nodeSlug, create) {
        /*
         * Populates a Div with node's participation data
         * 
         */

        if (create === "true") {
            nodeDiv = document.createElement('div');
            nodeDiv.id = nodeSlug;
        }
        console.log(nodeSlug)
        var node = getData(window.__BASEURL__ + 'api/v1/nodes/' + nodeSlug);
        var nodeName = node.name;
        var nodeAddress = node.address;
        var nodeLayer = node.layer;

        for (var i in layers) {
            if (layers[i].id == nodeLayer) {
                var layerSlug = (layers[i].slug)
            }
        }
        var tmplMarkup = $('#tmplNodePopup').html();
        var compiledTmpl = _.template(tmplMarkup, {
            node: nodeName,
            address: nodeAddress
        });
        $(nodeDiv).append(compiledTmpl);

        if (participation === "True") {

            var nodeSettings = getData(window.__BASEURL__ + 'api/v1/nodes/' + nodeSlug + '/participation_settings/');
            var layerSettings = getData(window.__BASEURL__ + 'api/v1/layers/' + layerSlug + '/participation_settings/');

            var layerVotingAllowed = layerSettings.participation_settings["voting_allowed"];
            var layerRatingAllowed = layerSettings.participation_settings["rating_allowed"];
            var layerCommentsAllowed = layerSettings.participation_settings["comments_allowed"];

            var nodeVotingAllowed = nodeSettings.participation_settings["voting_allowed"];
            var nodeRatingAllowed = nodeSettings.participation_settings["rating_allowed"];
            var nodeCommentsAllowed = nodeSettings.participation_settings["comments_allowed"];

            var node = getData(window.__BASEURL__ + 'api/v1/nodes/' + nodeSlug + '/participation/');

            var nodeRatingCount = node.participation.rating_count;
            var nodeLikes = node.participation.likes;
            var nodeDislikes = node.participation.dislikes;
            var nodeVoteCount = nodeLikes + nodeDislikes;
            var nodeComments = node.participation.comment_count;

            nodeRatingAVG = node.participation.rating_avg;

            if (layerRatingAllowed && nodeRatingAllowed == true) {
                var tmplMarkup = $('#tmplNodePopupRating').html();
                var compiledTmpl = _.template(tmplMarkup);
                $(nodeDiv).append(compiledTmpl);
            }

            if (layerVotingAllowed && nodeVotingAllowed == true) {
                var tmplMarkup = $('#tmplNodePopupVoting').html();
                var compiledTmpl = _.template(tmplMarkup, {
                    nodeSlug: nodeSlug,
                    likes: nodeLikes,
                    dislikes: nodeDislikes
                });
                $(nodeDiv).append(compiledTmpl);
            }

            if (layerCommentsAllowed && nodeCommentsAllowed == true) {
                var tmplMarkup = $('#tmplNodePopupComments').html();
                var compiledTmpl = _.template(tmplMarkup, {
                    nodeSlug: nodeSlug,
                    comments: nodeComments
                });
                $(nodeDiv).append(compiledTmpl);
            }

            populateRating(nodeSlug, nodeRatingAVG)
        }

        return (nodeDiv, nodeRatingAVG)

    }
    
    function getParticipationData(){
        window.nodeParticipation = getData(window.__BASEURL__ + 'api/v1/nodes/' + nodeSlug + '/participation/');
    }
    
    function showVotes(likes,dislikes){
        var tmplMarkup = $('#tmplOpen311Votes').html();
        var compiledTmpl = _.template(tmplMarkup, {
            likes: likes,
            dislikes:dislikes
        });
        $("#votesContainer").html('')
        $("#votesContainer").append(compiledTmpl);
        $("#likeButton").on("click",function(){
				       postVote(nodeId, 1);
				  });
        $("#unlikeButton").on("click",function(){
				       postVote(nodeId, -1);
				  });
    }

    function showComments(nodeSlug,comments_count) {
        url = window.__BASEURL__ + 'api/v1/nodes/' + nodeSlug + '/comments/?format=json';
        var comments = getData(url);
        var tmplMarkup = $('#tmplComments').html();
        var compiledTmpl = _.template(tmplMarkup, {
            comments: comments,
            node: nodeId,
            comments_count: comments_count
        });
        $("#commentsContainer").html('');
        $("#commentsContainer").append(compiledTmpl);
        $("#post_comments").on("click",function(){
				       postComment(nodeId);
				  });

    }
    
    

    /* INSERTION OF NODES' PARTICIPATION DATA 
     * ====================================== */

    function reloadNodeDiv(nodeSlug) {
        var nodeDiv = $("#" + nodeSlug);
        $(nodeDiv).html('');
        populateNodeDiv(nodeSlug, 0);
        populateRating(nodeSlug, nodeDiv, nodeRatingAVG);
    }

    function postComment(nodeID) {
        /*
         * post a comment
         */
        var comment = $("#commentText").val();
        var ok = confirm("Add comment for this node?");
        if (ok == true) {
            $.ajax({
                type: "POST",
                url: window.__BASEURL__ + 'api/v1/open311/requests/',
                data: {
                    "service_code": "comment",
                    "node": nodeID,
                    "text": comment
                },
                dataType: 'json',
                success: function (response) {
                    getParticipationData()
                    
                    showComments(nodeSlug,nodeParticipation.participation.comment_count);
                    $("#comment_messages").html("Thanks for your comment");
                    
                },
                error: function (jqXHR,error, errorThrown) {
                    console.log(jqXHR)
                    $("#comment_error_messages").html(jqXHR.responseText);
                }
                

            });
        
        }
        
    }

    function postVote(nodeID, vote) {
        /*
         * post a vote
         */
        var ok = confirm("Add vote " + vote + " for this node?");
        if (ok == true) {
            $.ajax({
                type: "POST",
                url: window.__BASEURL__ + 'api/v1/open311/requests/',
                data: {
                    "service_code": "vote",
                    "node": nodeID,
                    "vote": vote
                },
                dataType: 'json',
                success: function (response) {
                    getParticipationData()
                    showVotes(nodeParticipation.participation.likes,nodeParticipation.participation.dislikes);
                    $("#vote_messages").html("Thanks for your vote");
                },
                error: function (jqXHR,error, errorThrown) {
                    console.log(jqXHR)
                    $("#vote_error_messages").html(jqXHR.responseText);
                }
                

            });
        }
    }

    function postRating(nodeSlug, rating) {
        /*
         * post a rating
         */
        var ok = confirm("Add rating " + rating + " for this node?");
        if (ok == true) {
            $.ajax({
                type: "POST",
                url: 'http://localhost:8000/api/v1/nodes/' + nodeSlug + '/ratings/',
                data: {
                    "value": rating
                },
                dataType: 'json',
                success: function (response) {
                    reloadNodeDiv(nodeSlug)
                    alert("Your rating has been added!");
                }
            });
        }
    }

    function populateRating(nodeSlug, nodeDiv, nodeRatingAVG) {
        /*
         * Show/update rating data of a node
         */
        x = $(nodeDiv).find('#star');
        $(x).raty({
            score: nodeRatingAVG,
            number: 10,
            path: $.myproject.STATIC_URL + 'interface/js/vendor/images',
            click: function (score) {
                postRating(nodeSlug, score);
            }
        });
    };

//login
function login() {
    user = $("#user").val();
    var password = $("#password").val();
    $.ajax({
        type: "POST",
        url: window.__BASEURL__ + "api/v1/account/login/",
        data: {
            "username": user,
            "password": password
        },
        dataType: 'json',
        success: function (response) {
            showLogout(user);
        }
    });
}

//logout
function logout() {
    $.ajax({
        type: "POST",
        url: window.__BASEURL__ + "api/v1/account/logout/",
        dataType: 'json',
        success: function (response) {
            showLogin();
        }

    });
}

function showLogin() {
    var tmplMarkup = $('#tmplLogin').html();
    var compiledTmpl = _.template(tmplMarkup);
    $('#userForm').html(compiledTmpl);
}

function showLogout(user) {
    var tmplMarkup = $('#tmplLogout').html();
    var compiledTmpl = _.template(tmplMarkup, user);
    $('#userForm').html(compiledTmpl);
}
