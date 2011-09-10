
//var map;
//var nodeshot.gmap.geocoder;
//var markersArray = {
//    'active' : [],
//    'potential': [],
//    'activeListeners': [],
//    'potentialListeners': [],
//    'hotspot': [],
//    'hotspotListeners': [],
//    'links': []
//};
//var nodeshot.gmap.newMarker;
//var nodeshot.gmap.newMarkerListener;
//var clickListener;
//var infoWindow = new google.maps.InfoWindow;


//function draw_nodes(status) {
//    // shortcut to the object we need
//    var data = nodeshot.nodes[status];
//    // marker icon depends on the status (green = active, blue = hotspot, orange = potential)
//    var image = nodeshot.url.media+'images/marker_'+status+'.png';
//    
//    for(var node in data) {
//        // save marker in current node object
//        var latlng = new google.maps.LatLng(data[node].lat, data[node].lng);
//        data[node].marker = new google.maps.Marker({
//            position: latlng,
//            map: nodeshot.gmap.map,
//            title: data[node].name,
//            icon: image
//        });
//        data[node].marker.slug = data[node].slug;
//        // show marker on gmap
//        data[node].marker.setMap(nodeshot.gmap.map);
//        // add event listener
//        data[node].listener = google.maps.event.addListener(data[node].marker, 'click',  clickMarker(data[node].marker, data[node]));
//    }
//    // draw links if status is active
//    if (status == status_choices.a) {
//        // cache length for upcount while loop
//        var len = nodes.links.length;
//        var ilen = len;
//        // determine which link quality calculation method we should use
//        var quality = nodeshot.layout.$linkQuality.find('input:checked').val();
//        // this is performant on modern browsers
//        while(--len){
//            // shortcut to link
//            var link = nodes.links[ilen-len];
//            // draw link from ... to ...
//            /*
//            writing
//                quality = 'dbm';
//                link[quality]
//            is the same as writing
//                link.dbm
//            */
//            draw_link(link.from_lat, link.from_lng, link.to_lat, link.to_lng, link[quality]);
//        }
//    }
//}

//function remove_markers(status) {
//    // loop over nodes with the specified status and remove them from gmap
//    for(var node in nodeshot.nodes[status]){
//        // remove from gmap
//        nodeshot.nodes[status][node].marker.setMap(null);
//        // remove listener
//        google.maps.event.removeListener(nodeshot.nodes[status][node].listener);
//    }
//}

//function getNodeState(nodeSlug) {
//    // repeat action for each possible status
//    for(var status in status_choices){
//        // loop over nodes with that status
//        for (var i = 0; i < nodes[status].length; i++){
//            // if node is found
//            if (nodes[status][i].slug == nodeSlug){
//                // return status
//                return status_choices[status];
//            }
//        }
//    }
//    //for (var i = 0; i < nodes.active.length; i++){
//    //    if (nodes.active[i].slug == nodeSlug){
//    //        return 'a';
//    //    }
//    //}
//    //for (var i = 0; i < nodes.hotspot.length; i++){ 
//    //    if (nodes.hotspot[i].slug == nodeSlug){
//    //        return 'h';
//    //    }
//    //}
//    //for (var i = 0; i < nodes.potential.length; i++){
//    //    if (nodes.potential[i].slug == nodeSlug){
//    //        return 'p';
//    //    }
//    //}
//    return 'n';
//}




//function findMarker(node) {
//    // if destination is a potential node and $potential is unchecked show potential nodes
//    nodeshot.gmap.check$potential(nodeshot.status_choices[node.status]);
//    // return google.maps.Marker object
//    return node.marker;
//}
//
//function mapGoTo(node) {
//    // get google.maps.Marker object
//    var marker = findMarker(node);
//    if (marker) {
//        // trigger click event
//        google.maps.event.trigger(marker, 'click');
//        // center gmap
//        nodeshot.gmap.map.panTo(marker.getPosition());
//        // zoom a little bit
//        nodeshot.gmap.map.setZoom(13);
//    } else {
//        // node not found
//        nodeshot.dialog.open('Il nodo non esiste.');
//    }
//}
//
///* remove the new marker (if exists) */
//function removeNewMarker(){
//    if (nodeshot.gmap.newMarker){ 
//        nodeshot.gmap.newMarker.setMap(null);
//    }
//    if (nodeshot.gmap.newMarkerListener){
//        google.maps.event.removeListener(nodeshot.gmap.newMarkerListener);
//    }
//    nodeshot.gmap.newMarker = null;
//    nodeshot.gmap.newMarkerListener = null;
//}
//
//function newNodeMarker(location) {
//        removeNewMarker();   
//        var marker = new google.maps.Marker({
//            position: location,
//            map: nodeshot.gmap.map,
//            icon: nodeshot.url.media+'images/marker_new.png'
//        });
//        var contentString = '<div id="confirm-new"><h2>Mi hai posizionato bene?</h2>'+
//            '<a href="javascript:nodeshot.node.add()" class="green">Si</a>'+
//            '<a href="javascript:removeNewMarker()" class="red">No</a></div>'
//
//        nodeshot.gmap.infoWindow = new google.maps.InfoWindow({
//            content: contentString
//        });
//        //map.setCenter(location);
//        nodeshot.gmap.infoWindow.open(nodeshot.gmap.map,marker); 
//        nodeshot.gmap.newMarkerListener = google.maps.event.addListener(marker, 'click', function() {
//            nodeshot.gmap.infoWindow.open(nodeshot.gmap.map,marker);
//        });
//        nodeshot.gmap.newMarker = marker;
//}



//function clickMarker(marker, node) {
//    return function() {
//        // if overlay is open
//        if(nodeshot.layout.$overlay){
//            // close it first
//            nodeshot.overlay.close();
//        }
//        nodeshot.overlay.addMask(0.7);
//        nodeshot.overlay.showLoading();
//        $.get(nodeshot.url.index+'node/info/'+node.id+'/', function(data) {
//            // remove listener in case it has already been set
//            if(nodeshot.gmap.infoWindow.domready){
//                google.maps.event.removeListener(nodeshot.gmap.infoWindow.domready);
//            }
//            // add listener to domready of infowindows - it will be triggered when the infoWindow is ready
//            nodeshot.gmap.infoWindow.domready = google.maps.event.addListener(nodeshot.gmap.infoWindow, 'domready', function(){
//                $(".tabs").tabs({
//                    // save height of first tab for comparison
//                    create: function(e, ui){
//                        // cache $(this)
//                        $this = $(this);
//                        // save height of active tab in nodeshot object
//                        nodeshot.tab0Height = $this.find('.ui-tabs-panel').eq($this.tabs('option', 'selected')).height();
//                    },
//                    // change height of tab if tab is shorter
//                    show: function(e, ui){
//                        // cache object
//                        $this = $(this);
//                        // if distance tab
//                        if($this.tabs('option', 'selected')===1){
//                            // cache object
//                            var tab = $this.find('.ui-tabs-panel').eq(1);
//                            // save this height
//                            nodeshot.tab1Height = tab.height();
//                            // compare and if first tab was higher set the same height
//                            if(nodeshot.tab0Height > nodeshot.tab1Height){
//                                tab.height(nodeshot.tab0Height);
//                            }
//                        }
//                    },
//                    // advanced tab
//                    select: function(e, ui){
//                        if(ui.tab.id=='advanced-link'){
//                            nodeshot.overlay.addMask(0.8, true);
//                            nodeshot.overlay.showLoading();
//                            $.get($(ui.tab).attr('data-url'), function(data) {
//                                // open overlay, closeOnClick = true
//                                nodeshot.overlay.open(data, true);
//                                // init controls
//                                nodeshot.advanced.init();
//                                // we are not using $.live() for performance reasons
//                                nodeshot.overlay.bindCancelButton();
//                                // todo
//                            });                            
//                        }
//                        return false
//                    }
//                });
//                nodeshot.contact.link();
//                var search_input = $('#distance-search');
//                nodeshot.layout.bindFocusBlur(search_input);
//                // Implements the search function
//                search_input.autocomplete({
//                    minLength: 3,
//                    source: function(req, add) {
//                        $.getJSON("search/"+req.term+'/', function(data) {
//                            if (data != null && data.length > 0){
//                                add(data);
//                            }
//                            else{
//                                add("");
//                            }
//                        });
//                    },
//                    select: function(event, ui) {
//                        nodeshot.distance.calculate({
//                            // TODO: storing stuff in infowindow might not be necessary
//                            from_name: nodeshot.gmap.infoWindow.node.name,
//                            from_slug: nodeshot.gmap.infoWindow.node.slug,
//                            from_lat: nodeshot.gmap.infoWindow.node.lat,
//                            from_lng: nodeshot.gmap.infoWindow.node.lng,
//                            to_name: ui.item.name,
//                            to_slug: ui.item.value,
//                            to_lat: ui.item.lat,
//                            to_lng: ui.item.lng,
//                            to_status: ui.item.status
//                        });
//                        search_input.val(ui.item.label)
//                        return false;
//                    }
//                });
//                $('#distance-select').change(function(){
//                    // cache $(this)
//                    $this = $(this);
//                    // split values in array
//                    var values = ($this.val()).split(';');
//                    //// replace comma
//                    var to_lat = (values[0]).replace(",",".");
//                    var to_lng = (values[1]).replace(",",".");
//                    var to_slug = values[2];
//                    var to_status = values[3]
//                    // calculate distance and add controls
//                    nodeshot.distance.calculate({
//                        from_name: nodeshot.gmap.infoWindow.node.name,
//                        from_slug: nodeshot.gmap.infoWindow.node.slug,
//                        from_lat: nodeshot.gmap.infoWindow.node.lat,
//                        from_lng: nodeshot.gmap.infoWindow.node.lng,
//                        to_name: $this.find('option[value="'+$this.val()+'"]').text(),
//                        to_slug: to_slug,
//                        to_lat: to_lat,
//                        to_lng: to_lng,
//                        to_status: to_status
//                    });
//                });
//                nodeshot.layout.setFullScreen();
//            });
//            nodeshot.gmap.infoWindow.setContent(data);
//            nodeshot.gmap.infoWindow.maxWidth = 500;
//            nodeshot.gmap.infoWindow.open(nodeshot.gmap.map, marker);
//            nodeshot.overlay.hideLoading();
//            // remove mask only if there isn't any dialog
//            if(!nodeshot.layout.$dialog){
//                nodeshot.overlay.removeMask();
//            }
//            nodeshot.gmap.infoWindow.node = node;
//        });
//    };
//} 

//function calc_distance(lat1, lon1, lat2, lon2, unit) {
//    var radlat1 = Math.PI * lat1/180;
//    var radlat2 = Math.PI * lat2/180;
//    var radlon1 = Math.PI * lon1/180;
//    var radlon2 = Math.PI * lon2/180;
//    var theta = lon1-lon2;
//    var radtheta = Math.PI * theta/180;
//    var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
//    dist = Math.acos(dist);
//    dist = dist * 180/Math.PI;
//    dist = dist * 60 * 1.1515;
//    if (unit=="K") { dist = dist * 1.609344 };
//    if (unit=="N") { dist = dist * 0.8684 };
//    return dist;
//}

//function draw_link(from_lat, from_lng, to_lat, to_lng, quality) {
//    // init local var
//    var color;
//    // determine color depending on link quality
//    if (quality==1){
//        color =  '#00ff00'; // Good
//    }
//    else if (quality==2){ 
//        color =  '#ffff00'; // Medium
//    }
//    else if (quality==3){
//        color =  '#ee0000'; // Bad
//    }
//    else if (quality==4){
//        color =  '#5f0060'; // used for distance calculations
//    }
//    // draw link on gmap
//    var link = new google.maps.Polyline({
//        // coordinates
//        path: [new google.maps.LatLng(from_lat, from_lng),new google.maps.LatLng(to_lat, to_lng)],
//        // line features
//        strokeColor: color,
//        strokeOpacity: 0.4,
//        strokeWeight: 5 
//    });
//    // show link on gmap
//    link.setMap(nodeshot.gmap.map);
//    if(quality==4){
//        return link;
//    }
//    return true;
//}

