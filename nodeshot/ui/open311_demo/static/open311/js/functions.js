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
            url: NS_311.__BASEURL__ + 'open311/requests.json?service_code=node&layer=' + layer,
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
        var marker = NS_311.markerMap[slug];
        populateOpen311Div(slug, "true");
        marker.addTo(map)
        marker.bindPopup(nodeDiv)
        marker.openPopup()
    })
}

//function loadLayers(layers) {
//    /*
//     * Takes all node of a layer and puts them on map in a Leaflet Clustered group
//     */
//    for (var i in layers) {
//        var color = layers[i].color;
//        var clusterClass = layers[i].slug; //CSS class with same name of the layer
//        //Creates a Leaflet cluster group styled with layer's colour
//        NS_311.mapClusters[layers[i].slug] = createCluster(clusterClass);
//        //Loads nodes in the cluster
//        var url = NS_311.__BASEURL__ + 'open311/requests.json?service_code=node&layer=' + layers[i].slug
//        var open311GeoJSON = new Geojson;
//        $.ajax({
//            url: url,
//            dataType: 'json',
//            success: function (response) {
//                open311GeoJSON.load(response, "long", "lat");
//                var newClusterLayer = loadNodes(layers[i].slug, open311GeoJSON, NS_311.colors[i]);
//                NS_311.mapClusters[layers[i].slug].addLayer(newClusterLayer);
//                //Adds cluster to map
//                map.addLayer(NS_311.mapClusters[layers[i].slug]);
//                //Creates map controls for the layer
//                var newClusterKey = "<span style='color:" + NS_311.colors[i] + "'>" + layers[i].name + "</span>";
//                //overlaymaps[newClusterKey] = NS_311.mapClusters[layers[i].slug];
//                //mapControl = L.control.layers(baseMaps, overlaymaps).addTo(map);
//                console.log( legend)
//                legend.addTo(map);
//
//
//            }
//        })
//
//
//    }
//    
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
        NS_311.mapClusters[layers[i].slug] = createCluster(clusterClass);
        //Loads nodes in the cluster
        var newClusterNodes = getData(NS_311.__BASEURL__ + 'open311/requests.json?service_code=node&layer=' + layers[i].slug);
        //Creates GeoJSON from JSON
        var open311GeoJSON = new Geojson;
        open311GeoJSON.load(newClusterNodes, "long", "lat")
        var newClusterLayer = loadNodes(layers[i].slug, open311GeoJSON, NS_311.colors[i]);
        NS_311.mapClusters[layers[i].slug].addLayer(newClusterLayer);
        //Adds cluster to map
        map.addLayer(NS_311.mapClusters[layers[i].slug]);
        //Creates map controls for the layer
        var newClusterKey = "<span style='color:" + NS_311.colors[i] + "'>" + layers[i].name + "</span>";
        overlaymaps[newClusterKey] = NS_311.mapClusters[layers[i].slug];
        allLayers[i] = NS_311.mapClusters[layers[i].slug];
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
                populateOpen311Div(feature.properties.service_request_id, "true");
                this.bindPopup(nodeDiv);
            });

        },
        pointToLayer: function (feature, latlng) {
            var marker = new
            L.circleMarker(latlng, {
                radius: 8,
                fillColor: NS_311.status_colors[feature.properties.status],
                color: color,
                weight: 3,
                opacity: 1,
                fillOpacity: 0.8
            });
            NS_311.markerMap[feature.properties.service_request_id] = marker;
            NS_311.markerStatusMap[feature.properties.status].push(marker)

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
    if (NS_311.markerToRemove) {
        map.removeLayer(NS_311.markerToRemove);
    }

    markerLocation = e.latlng
    marker = new L.Marker(markerLocation);
    NS_311.markerToRemove = marker
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
    var long = arrayLatLng[1].slice(0, -1);
    var latlng = new L.LatLng(lat, long);

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
        $("#requestLng").val(long);
        $("#requestLat").val(lat);
        $('#requestLng').attr('readonly', true);
        $('#requestLat').attr('readonly', true);
        getAddress(lat, long);
        $("#requestForm").submit(function (event) {

            //disable the default form submission
            event.preventDefault();
            //grab all form data  
            var formData = new FormData($(this)[0]);
            var layer_inserted = $(this).serializeArray()[1]['value']

            $.ajax({
                url: NS_311.__BASEURL__ + 'open311/requests.json',
                type: 'POST',
                data: formData,
                async: false,
                cache: false,
                contentType: false,
                processData: false,
                success: function (returndata) {
                    var circle = L.circleMarker(latlng, {
                        radius: 8,
                        fillColor: NS_311.status_colors['open'],
                        //color: color,
                        weight: 3,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(map);
                    var newMarker = L.marker(latlng);
                    NS_311.mapClusters[layer_inserted].addLayer(newMarker);
                    NS_311.markerMap[returndata] = newMarker;
                    NS_311.markerStatusMap['open'].push(newMarker)
                    legend.removeFrom(map)
                    legend.addTo(map)
                    popupMessage = "Request has been inserted<br>"
                    popupMessage += "<strong>Request ID: </strong>" + returndata
                    circle.bindPopup(popupMessage).openPopup();
                    map.panTo(latlng)
                    $('#serviceRequestForm').hide("fast", function () {
                        $('#overlay').fadeOut('fast');
                    })
                },
                error: function (jqXHR, error, errorThrown) {
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

    var node = getData(NS_311.__BASEURL__ + 'open311/requests/' + nodeSlug + '.json');
    var status = node.status;
    var nodeLayer = node.layer;
    var requestID = nodeSlug;

    var tmplMarkup = $('#tmplOpen311Popup').html();
    var compiledTmpl = _.template(tmplMarkup, {
        service_request_id: requestID,
        status: status,
    });
    $(nodeDiv).append(compiledTmpl);
    $(nodeDiv).on('click', function () {
        showRequestDetail(requestID, node)
    });


    return (nodeDiv, NS_311.nodeRatingAVG)

}

function showRequestDetail(requestID, node) {
    $('#overlay').fadeIn('fast', function () {
        $('#RequestDetails').show();
        $('#RequestDetails').html('<a class="boxclose"  id="RequestDetailsClose"></a>');
        $('#RequestDetailsClose').on("click", function () {
            $('#RequestDetails').hide("fast", function () {
                $('#overlay').fadeOut('fast');
            });
        });
        var tmplMarkup = $('#tmplOpen311RequestBox').html();
        var compiledTmpl = _.template(tmplMarkup, {});
        $("#RequestDetails").append(compiledTmpl);

        //$("#MainPage").hide();
        //$("#RequestDetails").show();
        NS_311.nodeSlug = node.slug
        NS_311.nodeId = requestID.split("-")[1];
        NS_311.layerSettings = getData(NS_311.__BASEURL__ + 'layers/' + node.layer_slug + '/participation_settings/');
        NS_311.nodeSettings = getData(NS_311.__BASEURL__ + 'nodes/' + node.slug + '/participation_settings/');
        NS_311.nodeParticipation = getData(NS_311.__BASEURL__ + 'nodes/' + node.slug + '/participation/');
        //getParticipationData()
        var request = getData(NS_311.__BASEURL__ + 'open311/requests/' + requestID + '.json');
        var tmplMarkup = $('#tmplOpen311Request').html();
        var compiledTmpl = _.template(tmplMarkup, {
            request: request,
            requestID: requestID,

        });
        $("#requestContainer").html('');
        $("#requestContainer").append(compiledTmpl);

        //Votes
        if (NS_311.nodeSettings.participation_settings.voting_allowed && NS_311.layerSettings.participation_settings.voting_allowed) {
            //console.log("Votes OK")
            showVotes(NS_311.nodeParticipation.participation.likes, NS_311.nodeParticipation.participation.dislikes)
        }

        //Comments       
        if (NS_311.nodeSettings.participation_settings.comments_allowed && NS_311.layerSettings.participation_settings.comments_allowed) {
            //console.log("Comments OK")
            showComments(NS_311.nodeSlug, NS_311.nodeParticipation.participation.comment_count);
        }

        //rating       
        if (NS_311.nodeSettings.participation_settings.rating_allowed && NS_311.layerSettings.participation_settings.rating_allowed) {
            //console.log("Rating OK")
            showRating(NS_311.nodeSlug, NS_311.nodeParticipation.participation.rating_avg, NS_311.nodeParticipation.participation.rating_count);
        }
    })
}

function showMainPage(requestID) {
    $("#MainPage").show();
    $("#RequestDetails").hide();
}

function getParticipationData() {
    NS_311.nodeParticipation = getData(NS_311.__BASEURL__ + 'nodes/' + NS_311.nodeSlug + '/participation/');
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
        postVote(NS_311.nodeId, 1);
    });
    $("#unlikeButton").on("click", function () {
        postVote(NS_311.nodeId, -1);
    });
}

function showComments(nodeSlug, comments_count) {
    url = NS_311.__BASEURL__ + 'nodes/' + nodeSlug + '/comments/?format=json';
    var comments = getData(url);
    var tmplMarkup = $('#tmplComments').html();
    var compiledTmpl = _.template(tmplMarkup, {
        comments: comments,
        node: NS_311.nodeId,
        comments_count: comments_count
    });
    $("#commentsContainer").html('');
    $("#commentsContainer").append(compiledTmpl);
    $("#post_comments").on("click", function () {
        postComment(NS_311.nodeId);
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
            url: NS_311.__BASEURL__ + 'open311/requests.json',
            data: {
                "service_code": "comment",
                    "node": nodeID,
                    "text": comment
            },
            dataType: 'json',
            success: function (response) {
                getParticipationData()

                showComments(NS_311.nodeSlug, NS_311.nodeParticipation.participation.comment_count);
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
            url: NS_311.__BASEURL__ + 'open311/requests.json',
            data: {
                "service_code": "vote",
                    "node": nodeID,
                    "vote": vote
            },
            dataType: 'json',
            success: function (response) {
                getParticipationData()
                showVotes(NS_311.nodeParticipation.participation.likes, NS_311.nodeParticipation.participation.dislikes);
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
            url: NS_311.__BASEURL__ + 'open311/requests.json',
            data: {
                "service_code": "rate",
                    "node": nodeID,
                    "value": rating
            },
            dataType: 'json',
            success: function (response) {
                getParticipationData()
                showRating(NS_311.nodeSlug, NS_311.nodeParticipation.participation.rating_avg, NS_311.nodeParticipation.participation.rating_count);
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
        width: 250,
        path: $.myproject.STATIC_URL + 'open311/js/vendor/images',
        click: function (score) {
            var nodeID = NS_311.nodeId;
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
        url: NS_311.__BASEURL__ + "account/login/",
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
        url: NS_311.__BASEURL__ + "account/logout/",
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