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
            url: window.__BASEURL__ + 'open311/requests?service_code=node&layer=' + layer,
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            success: function (result) {
                addToList(result)
            },
        })
    }
}

function addToList(data) {
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
        populateOpen311Div(slug, "true");
        marker.addTo(map)
        marker.bindPopup(nodeDiv)
        marker.openPopup()
    })
}

/* INSERTION OF NODES ON MAP ON PAGE LOAD
 * ====================================== */

//function loadLayersArea(layers) {
//    /*
//     * Puts layer areas on map
//     */
//    var allLayersArea = []
//    for (var i in layers.features) {
//
//        var newArea = L.geoJson(layers.features[i], {
//            style: {
//                weight: 1,
//                opacity: 1,
//                color: 'black',
//                clickable: false,
//                dashArray: '3',
//                fillOpacity: 0.2,
//                fillColor: layers.features[i].properties.color
//            }
//        }).addTo(map);
//        var newAreaKey = "<span style='font-weight:bold;color:" + layers.features[i].properties.color + "'>" + layers.features[i].properties.name + " Area</span>";
//        overlaymaps[newAreaKey] = newArea;
//        allLayersArea[i] = newArea;
//    }
//    return allLayersArea;
//}

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
        window.markerStatusMap[layers[i].slug] = {
            "open": [],
            "closed": []
        }
        //var newCluster = window.mapClusters[layers[i].slug];
        //Loads nodes in the cluster
        var newClusterNodes = getData(window.__BASEURL__ + 'open311/requests?service_code=node&layer=' + layers[i].slug);
        var GeoJSON = new geojsonColl();
        for (var n in newClusterNodes) {

            var feature = new featureConstructor;
            feature.geometry.coordinates = [newClusterNodes[n].lng,
            newClusterNodes[n].lat]
            feature.properties = newClusterNodes[n]
            GeoJSON.features.push(feature)


        }

        var newClusterLayer = loadNodes(layers[i].slug, GeoJSON, colors[i]);
        window.mapClusters[layers[i].slug].addLayer(newClusterLayer);
        //Adds cluster to map
        map.addLayer(window.mapClusters[layers[i].slug]);
        //Creates map controls for the layer
        var newClusterKey = "<span style='color:" + colors[i] + "'>" + layers[i].name + "</span>";
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


function loadNodes(layer_slug, newClusterNodes, color) {
    /*
     * Load nodes in cluster group and defines click properties for the popup window
     */
    var layer = L.geoJson(newClusterNodes, {

        onEachFeature: function (feature, layer) {
            layer.on('click', function (e) {
                populateOpen311Div(feature.properties.request_id, "true");
                this.bindPopup(nodeDiv);
            });

        },
        pointToLayer: function (feature, latlng) {
            var marker = new
            L.circleMarker(latlng, {
                radius: 8,
                fillColor: window.status_colors[feature.properties.status],
                color: color,
                weight: 3,
                opacity: 1,
                fillOpacity: 0.8
            });
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

function openForm(marker) {
    var latlngToString = marker.toString();
    var arrayLatLng = latlngToString.split(",");
    var lat = arrayLatLng[0].slice(7);
    var lng = arrayLatLng[1].slice(0, -1);
    var latlng = new L.LatLng(lat, lng);

    $('#overlay').fadeIn('fast', function () {
        $('#serviceRequestForm').show();
        $('#serviceRequestForm').html('<a class="boxclose"  id="boxclose"></a>');
        $('#boxclose').on("click", function () {
            $('#serviceRequestForm').hide("fast", function () {
                $('#overlay').fadeOut('fast');
            });
        });
        var tmplMarkup = $('#tmplInsertNode').html();
        var compiledTmpl = _.template(tmplMarkup, {
            layers: layers
        });
        var nodeInsertDiv = $("<div>", {
            id: "serviceRequestForm"
        });

        $('#serviceRequestForm').append(compiledTmpl);
        $("#requestLng").val(lng);
        $("#requestLat").val(lat);
        $('#requestLng').attr('readonly', true);
        $('#requestLat').attr('readonly', true);
        getAddress(lat, lng);
        $("#requestForm").submit(function (event) {

            //disable the default form submission
            event.preventDefault();
            //grab all form data  
            var formData = new FormData($(this)[0]);
            var layer_inserted = $(this).serializeArray()[1]['value']

            $.ajax({
                url: window.__BASEURL__ + 'open311/requests/',
                type: 'POST',
                data: formData,
                async: false,
                cache: false,
                contentType: false,
                processData: false,
                success: function (returndata) {
                    var circle = L.circleMarker(latlng, {
                radius: 8,
                fillColor: window.status_colors['open'],
                //color: color,
                weight: 3,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
                    newMarker = L.marker(latlng);
                    window.mapClusters[layer_inserted].addLayer(newMarker);
                    window.markerMap[returndata] = newMarker;
                    popupMessage = "Request has been inserted<br>"
                    popupMessage += "<strong>Request ID: </strong>"+ returndata
                    circle.bindPopup(popupMessage).openPopup();
                    map.panTo(latlng)
                    $('#serviceRequestForm').hide("fast", function () {
                        $('#overlay').fadeOut('fast');
                    })
                },
                error: function (jqXHR, error, errorThrown) {
                    //console.log(jqXHR)
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

    var node = getData(window.__BASEURL__ + 'open311/requests/' + nodeSlug);
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
    $(nodeDiv).on('click',function(){showRequestDetail(requestID,node)});
    

    return (nodeDiv, nodeRatingAVG)

}

function showRequestDetail(requestID,node) {
    $("#MainPage").hide();
    $("#RequestDetails").show();
    window.nodeSlug = node.slug
    window.nodeId = requestID.split("-")[1];
    window.layerSettings = getData(window.__BASEURL__ + 'layers/' + node.layer + '/participation_settings/');
    window.nodeSettings = getData(window.__BASEURL__ + 'nodes/' + node.slug + '/participation_settings/');
    window.nodeParticipation = getData(window.__BASEURL__ + 'nodes/' + node.slug + '/participation/');
    getParticipationData()
    var request = getData(window.__BASEURL__ + 'open311/requests/' + requestID); 
    var tmplMarkup = $('#tmplOpen311Request').html();
    var compiledTmpl = _.template(tmplMarkup, {
            request: request,
            requestID: requestID,
            
        });
        $("#request").html(compiledTmpl);

//Votes
if (nodeSettings.participation_settings.voting_allowed && layerSettings.participation_settings.voting_allowed) {
    //console.log("Votes OK")
    showVotes(nodeParticipation.participation.likes,nodeParticipation.participation.dislikes)
}

//Comments       
if (nodeSettings.participation_settings.comments_allowed && layerSettings.participation_settings.comments_allowed) {
    //console.log("Comments OK")
    showComments(nodeSlug,nodeParticipation.participation.comment_count); 
}

//Comments       
if (nodeSettings.participation_settings.rating_allowed && layerSettings.participation_settings.rating_allowed) {
    //console.log("Rating OK")
    showRating(nodeSlug,nodeParticipation.participation.rating_avg,nodeParticipation.participation.rating_count); 
}

}

function showMainPage(requestID) {
    $("#MainPage").show();
    $("#RequestDetails").hide();
}

function getParticipationData() {
    window.nodeParticipation = getData(window.__BASEURL__ + 'nodes/' + nodeSlug + '/participation/');
}

function showVotes(likes, dislikes) {
    var tmplMarkup = $('#tmplOpen311Votes').html();
    var compiledTmpl = _.template(tmplMarkup, {
        likes: likes,
        dislikes: dislikes
    });
    $("#votesContainer").html('')
    $("#votesContainer").append(compiledTmpl);
    $("#likeButton").on("click", function () {
        postVote(nodeId, 1);
    });
    $("#unlikeButton").on("click", function () {
        postVote(nodeId, -1);
    });
}

function showComments(nodeSlug, comments_count) {
    url = window.__BASEURL__ + 'nodes/' + nodeSlug + '/comments/?format=json';
    var comments = getData(url);
    var tmplMarkup = $('#tmplComments').html();
    var compiledTmpl = _.template(tmplMarkup, {
        comments: comments,
        node: nodeId,
        comments_count: comments_count
    });
    $("#commentsContainer").html('');
    $("#commentsContainer").append(compiledTmpl);
    $("#post_comments").on("click", function () {
        postComment(nodeId);
    });

}

function showRating(nodeSlug, nodeRatingAVG, nodeRatingCount) {
    var tmplMarkup = $('#tmplNodePopupRating').html();
    var compiledTmpl = _.template(tmplMarkup, {
        'rating': nodeRatingAVG,
            'votes': nodeRatingCount
    });
    $("#ratingContainer").html('')
    $("#ratingContainer").append(compiledTmpl);
    populateRating(nodeSlug, 'rating', nodeRatingAVG)
}

/* INSERTION OF NODES' PARTICIPATION DATA 
 * ====================================== */

function postComment(nodeID) {
    /*
     * post a comment
     */
    var comment = $("#commentText").val();
    var ok = confirm("Add comment for this node?");
    if (ok == true) {
        $.ajax({
            type: "POST",
            url: window.__BASEURL__ + 'open311/requests/',
            data: {
                "service_code": "comment",
                    "node": nodeID,
                    "text": comment
            },
            dataType: 'json',
            success: function (response) {
                getParticipationData()

                showComments(nodeSlug, nodeParticipation.participation.comment_count);
                $("#comment_messages").html("Thanks for your comment");

            },
            error: function (jqXHR, error, errorThrown) {
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
            url: window.__BASEURL__ + 'open311/requests/',
            data: {
                "service_code": "vote",
                    "node": nodeID,
                    "vote": vote
            },
            dataType: 'json',
            success: function (response) {
                getParticipationData()
                showVotes(nodeParticipation.participation.likes, nodeParticipation.participation.dislikes);
                $("#vote_messages").html("Thanks for your vote");
            },
            error: function (jqXHR, error, errorThrown) {
                $("#vote_error_messages").html(jqXHR.responseText);
            }


        });
    }
}

function postRating(nodeID, rating) {
    /*
     * post a rating
     */
    var ok = confirm("Add rating " + rating + " for this node?");
    if (ok == true) {
        $.ajax({
            type: "POST",
            url: window.__BASEURL__ + 'open311/requests/',
            data: {
                "service_code": "rate",
                    "node": nodeID,
                    "value": rating
            },
            dataType: 'json',
            success: function (response) {
                getParticipationData()
                showRating(nodeSlug, nodeParticipation.participation.rating_avg, nodeParticipation.participation.rating_count);
                $("#rating_messages").html("Thanks for your rating");
            },
            error: function (jqXHR, error, errorThrown) {
                $("#rating_error_messages").html(jqXHR.responseText);
            }
        });
    }
}

function populateRating(nodeID, nodeDiv, nodeRatingAVG) {
    /*
     * Show/update rating data of a node
     */
    var x = $(nodeDiv).find('#star');
    $("#star").raty({
        score: nodeRatingAVG,
        number: 10,
        path: $.myproject.STATIC_URL + 'open311/js/vendor/images',
        click: function (score) {
            var nodeID = window.nodeId;
            //console.log(nodeID)
            postRating(nodeID, score);
        }
    });
};

//login
function login() {
    user = $("#user").val();
    var password = $("#password").val();
    $.ajax({
        type: "POST",
        url: window.__BASEURL__ + "account/login/",
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
        url: window.__BASEURL__ + "account/logout/",
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