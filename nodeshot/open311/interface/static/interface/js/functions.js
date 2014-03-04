var csrftoken = $.getCookie('csrftoken');
var markerToRemove //If users insert a new marker previous one has to be deleted from map
var nodeRatingAVG // Rating data has to be globally available for rating plugin to correctly work
var markerMap = {} //Object holding all nodes'slug and a reference to their marker

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
            populateRating(slug,nodeDiv,nodeRatingAVG)
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
            var newCluster = createCluster(clusterClass);
            //Loads nodes in the cluster
            //newClusterNodes = getData(window.__BASEURL__ + 'api/v1/layers/' + layers[i].slug + '/nodes.geojson');
            var newClusterNodes = getData(window.__BASEURL__ + 'api/v1/open311/requests?service_code=node&layer='+layers[i].slug );
            var GeoJSON= new geojsonColl();
                for (var n in newClusterNodes){
                            
                                    var feature = new featureConstructor;
                                    feature.geometry.coordinates = [newClusterNodes[n].lng,
                                                                   newClusterNodes[n].lat]
                                    feature.properties = newClusterNodes[n]
                                    GeoJSON.features.push(feature)
                                        
    
                                }
            
            var newClusterLayer = loadNodes(GeoJSON, color);
            newCluster.addLayer(newClusterLayer);
            //Adds cluster to map
            map.addLayer(newCluster);
            //Creates map controls for the layer
            var newClusterKey = "<span style='color:#0000ff'>" + layers[i].name + "</span>";
            overlaymaps[newClusterKey] = newCluster;
            allLayers[i] = newCluster;
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


    function loadNodes(newClusterNodes, color) {
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
                    radius: 6,
                    fillColor: color,
                    color: color,
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
                //console.log(feature.properties.name)
                window.markerMap[feature.properties.request_id] = marker;
                //console.log(markerMap[feature.properties.slug])
                //console.log(markerMap)

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
        openInsertDiv(marker);
        map.closePopup();
        //$("#insertMarker").html('');
        ////check if point is contained in more than one layer
        //var areaLayer = L.geoJson(geojsonlayers);
        //var results = leafletPip.pointInLayer(markerLocation, areaLayer, false);
        //// 0=point not in Layers, 1= point in 1 layer, default = point in multiple layers
        //switch (results.length) {
        //    case 0:
        //        var noAreaLayers = [];
        //        for (var i in layers) {
        //            if (layers[i].area === null) {
        //                noAreaLayers.push(layers[i]);
        //            }
        //
        //        }
        //        var tmplMarkup = $('#tmplcheckArea').html();
        //        var compiledTmpl = _.template(tmplMarkup, {
        //            choices: noAreaLayers
        //        });
        //        $("#insertMarker").append(compiledTmpl);
        //        $("#sendLayer").click(function () {
        //            var layerValues = $("input[name=\'layer\']:checked").val().split(",");
        //            openInsertDiv(marker, layerValues[0], layerValues[1]);
        //            $('.leaflet-popup-content-wrapper').hide()
        //        });
        //        break;
        //    case 1:
        //        openInsertDiv(marker, results[0].feature.properties.id, results[0].feature.properties.name);
        //        map.closePopup();
        //        break;
        //    default:
        //        var FoundedLayers = [];
        //        for (var i in results) {
        //            console.log(results[i].feature.properties.name);
        //            FoundedLayers.push(results[i].feature.properties);
        //        };
        //        var tmplMarkup = $('#tmplcheckArea').html();
        //        var compiledTmpl = _.template(tmplMarkup, {
        //            choices: FoundedLayers
        //        });
        //        $("#insertMarker").append(compiledTmpl);
        //        $("#sendLayer").click(function () {
        //
        //            var layerValues = $("input[name=\'layer\']:checked").val().split(",");
        //            openInsertDiv(marker, layerValues[0], layerValues[1]);
        //            $('#tmplcheckArea').hide()
        //        });
        //}

    }

    function openInsertDiv(latlng, layerID, layerName) {
        /*
         *Creates node's insertion form
         */
        var latlngToString = latlng.toString();
        var arrayLatLng = latlngToString.split(",");
        var lat = arrayLatLng[0].slice(7);
        var lng = arrayLatLng[1].slice(0, -1);

        var tmplMarkup = $('#tmplInsertNode').html();
        var compiledTmpl = _.template(tmplMarkup);
        var nodeInsertDiv = $("<div>", {
            id: "nodeInsertDiv"
        });

        $(nodeInsertDiv).html(compiledTmpl);
        $("#valori").html(nodeInsertDiv)
        $("#nodeToInsertLng").val(lng);
        $("#nodeToInsertLat").val(lat);
        $("#layerToInsert").val(layerName);
        $("#layerIdToInsert").val(layerID);
        $('#layerToInsert').attr('readonly', true);
        $('#nodeToInsertLng').attr('readonly', true);
        $('#nodeToInsertLat').attr('readonly', true);

        getAddress();

    }

    function postNode() {
        /*
         * Inserts node in DB and displays it on map
         */
        var nodeToInsert = {}
        var lng = $("#nodeToInsertLng").val();
        var lat = $("#nodeToInsertLat").val();
        var latlngToInsert = lat + '\,' + lng;
        nodeToInsert["service_code"] = "node"
        nodeToInsert["layer"] = "rome";
        nodeToInsert["name"] = $("#nodeToInsertName").val();
        nodeToInsert["slug"] = convertToSlug($("#nodeToInsertName").val())
        nodeToInsert["address"] = $("#nodeToInsertAddress").val();
        nodeToInsert["lat"] = lat
        nodeToInsert["lng"] = lng
        console.log(nodeToInsert)
        var latlng = new L.LatLng(lat, lng);
        var ok = confirm("Add service request?");
        if (ok == true) {
            $.ajax({
                type: "POST",
                url: window.__BASEURL__ + 'api/v1/open311/requests/',
                data: nodeToInsert,
                dataType: 'json',
                success: function (response) {
                    //Reload map to include new node, this should be definetely improved
                    alert('success')
                    clearLayers();
                    map.removeControl(mapControl)
                    mapLayersArea = loadLayersArea(geojsonlayers);
                    mapLayersNodes = loadLayers(layers);
                    mapControl = L.control.layers(baseMaps, overlaymaps).addTo(map);
                    newMarker = L.marker(latlng).addTo(map);
                    //populateNodeDiv(nodeToInsert["slug"],"true");
                    newMarker.bindPopup("Node added").openPopup();
                    map.panTo(latlng)
                    //newMarker.bindPopup(nodeDiv).openPopup();
                    $("#nodeInsertDiv").html('Node inserted');
                    //populateRating(nodeToInsert["slug"],nodeDiv,nodeRatingAVG);

                },
                error: function(){
                    alert('error');
                    //return(false);
                }

            });
        }
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


    function showComments(nodeSlug) {
        /*
         * Populates a Div with node's comments
         */

        $("#valori").html('');
        var commentsDiv = $("<div>", {
            id: "comments"
        });
        url = window.__BASEURL__ + 'api/v1/nodes/' + nodeSlug + '/comments/?format=json';
        var comments = getData(url);
        var tmplMarkup = $('#tmplComments').html();
        var compiledTmpl = _.template(tmplMarkup, {
            comments: comments,
            node: nodeSlug
        }); //Template should also get node name 
        $(commentsDiv).html(compiledTmpl);

        $("#valori").append(commentsDiv);

        pager = new Imtech.Pager(); //Paging of comments in div
        pager.paragraphsPerPage = 5; // set amount elements per page
        pager.pagingContainer = $('#comment'); // set of main container
        pager.paragraphs = $('div.comment_div', pager.pagingContainer); // set of required containers
        pager.showPage(1);

    }

    /* INSERTION OF NODES' PARTICIPATION DATA 
     * ====================================== */

    function reloadNodeDiv(nodeSlug) {
        var nodeDiv = $("#" + nodeSlug);
        $(nodeDiv).html('');
        populateNodeDiv(nodeSlug, 0);
        populateRating(nodeSlug, nodeDiv, nodeRatingAVG);
    }

    function postComment(nodeSlug) {
        /*
         * post a comment
         */
        var comment = $("#commentText").val();
        var ok = confirm("Add comment for this node?");
        if (ok == true) {
            $.ajax({
                type: "POST",
                url: window.__BASEURL__ + 'api/v1/nodes/' + nodeSlug + '/comments/',
                data: {
                    "text": comment
                },
                dataType: 'json',
                success: function (response) {
                    reloadNodeDiv(nodeSlug)
                    showComments(nodeSlug);
                    alert("Your comment has been added!");
                }

            });
        }
    }

    function postVote(nodeSlug, vote) {
        /*
         * post a vote
         */
        var ok = confirm("Add vote " + vote + " for this node?");
        if (ok == true) {
            $.ajax({
                type: "POST",
                url: 'http://localhost:8000/api/v1/nodes/' + nodeSlug + '/votes/',
                data: {
                    "vote": vote
                },
                dataType: 'json',
                success: function (response) {
                    reloadNodeDiv(nodeSlug)
                    alert("Your vote has been added!");
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
