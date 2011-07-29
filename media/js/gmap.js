var nodes = [];
var map;
var geocoder;
var markersArray = {
    'active' : [],
    'potential': [],
    'activeListeners': [],
    'potentialListeners': [],
    'hotspot': [],
    'hotspotListeners': [],
    'links': []
};
var newMarker;
var newMarkerListenerHandle;
var clickListenerHandle;
var infoWindow = new google.maps.InfoWindow;
var distanceL;

function getget(name) {
  var q = document.location.search;
  var i = q.indexOf(name + '=');

  if (i == -1) {
    return false;
  }

  var r = q.substr(i + name.length + 1, q.length - i - name.length - 1);

  i = r.indexOf('&');

  if (i != -1) {
    r = r.substr(0, i);
  }

  return r.replace(/\+/g, ' ');
}

function getNodeState(nodeName) {
   for (var i = 0; i < nodes.active.length; i++) 
        if (nodes.active[i].name == nodeName)
            return 'a';
    for (var i = 0; i < nodes.hotspot.length; i++) 
        if (nodes.hotspot[i].name == nodeName)
            return 'h';
   for (var i = 0; i < nodes.potential.length; i++) 
        if (nodes.potential[i].name == nodeName)
            return 'p';
    return 'n'
}

function findMarker(nodeName) {
    var nodeStatus = getNodeState(nodeName);
    if (nodeStatus == 'a' &&  ! $('#active').is(':checked') ) {
        $('#active').attr('checked', true);
        draw_nodes('a');
    } else if (nodeStatus == 'h' &&  ! $('#hotspot').is(':checked') ) {
        $('#hotspot').attr('checked', true);
        draw_nodes('h');
    } else if (nodeStatus == 'p' &&  ! $('#potential').is(':checked') ) {
        $('#potential').attr('checked', true);
        draw_nodes('p');
    }
    if (nodeStatus == 'a')
        marray = markersArray.active;
    else if (nodeStatus == 'h')
        marray= markersArray.hotspot;
    else if (nodeStatus == 'p')
        marray= markersArray.potential;
    else 
        return;
    for (var i = 0; i <  marray.length; i++) {
        if (marray[i].getTitle() == nodeName)
            return marray[i]
    }
    return null;
}

function mapGoTo(nodeName) {
    var marker = findMarker(nodeName);
    if (marker) {
        google.maps.event.trigger(marker, "click");
        map.panTo(marker.getPosition());
        map.setZoom(13);
    } else {
        alert('il nodo non esiste!')
    }
}

/* remove the new marker (if exists) */
function removeNewMarker(){
    if (newMarker) 
        newMarker.setMap(null);
    if (newMarkerListenerHandle) 
        google.maps.event.removeListener(newMarkerListenerHandle);
    newMarker = null;
    newMarkerListenerHandle = null;
}

function newNodeMarker(location) {
        removeNewMarker();   
        marker = new google.maps.Marker({
            position: location,
            map: map,
            icon: __project_home__+'media/images/marker_new.png'
        });
        var contentString = '<div id="confirm-new"><h2>Mi hai posizionato bene?</h2>'+
            '<a href="javascript:insertNodeInfo()" class="green">Si</a>'+
            '<a href="javascript:removeNewMarker()" class="red">No</a></div>'

        var infowindow = new google.maps.InfoWindow({
            content: contentString
        });
        //map.setCenter(location);
        infowindow.open(map,marker); 
        newMarkerListenerHandle = google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map,marker);
        });
        newMarker = marker;
}

function initialize_map() {
    var latlng = new google.maps.LatLng(__center__.lat, __center__.lng);

    var myOptions = {
        zoom: 12,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    geocoder = new google.maps.Geocoder();
    
    if(!__center__.is_default){
        intervalId = setInterval(function(){
            if(nodes.active!=undefined){
                clearInterval(intervalId);
                mapGoTo(__center__.node);
            }
        }, 500);
    }
}

function handleMarkerClick(marker, name) {
  return function() {
    $.get(__project_home__+'info_window/' + name, function(data) {
        infoWindow.setContent(data);
        infoWindow.open(map, marker);
        setTimeout(function(){ $(".tabs").tabs(); }, 100);
    } );
  };
} 

function calc_distance(lat1, lon1, lat2, lon2, unit) {
    var radlat1 = Math.PI * lat1/180;
    var radlat2 = Math.PI * lat2/180;
    var radlon1 = Math.PI * lon1/180;
    var radlon2 = Math.PI * lon2/180;
    var theta = lon1-lon2;
    var radtheta = Math.PI * theta/180;
    var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
    dist = Math.acos(dist);
    dist = dist * 180/Math.PI;
    dist = dist * 60 * 1.1515;
    if (unit=="K") { dist = dist * 1.609344 };
    if (unit=="N") { dist = dist * 0.8684 };
    return dist;
    
}

function draw_link(flat, flng, tlat, tlng, quality) {

    var linkCoordinates = [
        new google.maps.LatLng(flat, flng),
        new google.maps.LatLng(tlat, tlng)
    ];
    var qualityColor = '#000000';
    if (quality==1) 
        qualityColor =  '#00ff00' //Good
    else if (quality==2) 
        qualityColor =  '#ffff00' //Medium
    else if (quality==3) 
        qualityColor =  '#ee0000' //Bad
    else if (quality==4) 
        qualityColor =  '#000000' //used for tested link

    var link = new google.maps.Polyline({
        path: linkCoordinates,
        strokeColor: qualityColor,
        strokeOpacity: 0.4,
        strokeWeight: 5 
    });
    link.setMap(map);
    markersArray.links.push(link);

}

function draw_nodes(type) {
    var marray;
    var image = '';
    
    if (type == 'a') {
        data = nodes.active;
        marray = markersArray.active;
        larray = markersArray.activeListeners;
        image = __project_home__+'media/images/marker_active.png';
    } else if (type == 'p') {
        data = nodes.potential;
        marray = markersArray.potential;
        larray = markersArray.potentialListeners;
        image = __project_home__+'media/images/marker_potential.png';
    } else if (type == 'h') {
        data = nodes.hotspot;
        marray = markersArray.hotspot;
        larray = markersArray.hotspotListeners;
        image = __project_home__+'media/images/marker_hotspot.png';
    }
    
    for (var i = 0; i < data.length; i++) { 
        var latlng = new google.maps.LatLng(data[i].lat, data[i].lng);
        marker = new google.maps.Marker({
            position: latlng,
            map: map,
            title: data[i].name,
            icon: image
        });
        marray.push(marker);
        marker.setMap(map);  
        
        var listenerHandle = google.maps.event.addListener(marker, 'click',  handleMarkerClick(marker, data[i].name) );
                
        larray.push(listenerHandle);
    }
    // draw links if type is active
    if (type == 'a') {
        for (var i = 0; i < nodes.links.length; i++) {
            if ($("input[name='link-quality-selector']:checked").val() == 'etx')
                draw_link(nodes.links[i].from_lat, nodes.links[i].from_lng, nodes.links[i].to_lat, nodes.links[i].to_lng, nodes.links[i].etx);
            else
                draw_link(nodes.links[i].from_lat, nodes.links[i].from_lng, nodes.links[i].to_lat, nodes.links[i].to_lng, nodes.links[i].dbm);
        }
    }
}

function remove_markers(type) {
    var marray;
    if (type == 'a') {
        marray = markersArray.active;
        larray = markersArray.activeListeners;
        for (i in markersArray.links)
            markersArray.links[i].setMap(null);
    } else if (type == 'h') {
        marray = markersArray.hotspot;
        larray = markersArray.hotspotListeners;
    } else if (type == 'p') {
        marray = markersArray.potential;
        larray = markersArray.potentialListeners;
    }
    for (i in marray) {
        google.maps.event.removeListener(larray[i]);
        marray[i].setMap(null);
    }
}

var nodeshotModal = function(message, callback){
    nodeshotMask();
    $('body').append('<div id="nodeshot-modal"><div id="nodeshot-modal-message">'+message+'</div><a class="button green" id="nodeshot-modal-close">ok</a></div>');
    var modal = $('#nodeshot-modal');
    modal.css({
        opacity: 0,
        display: 'block',
        left: ($(window).width() - modal.width()) / 2,
        top: ($(window).height() - modal.height()) / 3
    }).animate({
        opacity: 1
    }, 500);
    
    $('#nodeshot-modal-close').click(function(){
        var dialog = $(this).parent();
        dialog.fadeOut(500, function(){
            dialog.remove();
        })
        nodeshotRemoveMask();
        if(callback){
            callback();
        }
    });
}

var nodeshotShowLoading = function(){
    img = $('#nodeshot-ajaxloader');
    img.css({
        left: ($(window).width()-img.width()) / 2,
        top: ($(window).height()-img.height()) / 2
    });
}

var nodeshotHideLoading = function(){
    $('#nodeshot-ajaxloader').css('top', '-9999px');
}

var nodeshotMask = function(opacity){
    if(document.getElementById("nodeshot-modal-mask") != null){
        return false;
    }
    if(!opacity){ opacity = 0.5 }
    $('body').append('<div id="nodeshot-modal-mask"></div>');
    $('#nodeshot-modal-mask').css({
        opacity: 0,
        display: 'block'
    }).animate({
        opacity: opacity
    }, 500);
}

var nodeshotRemoveMask = function(){
    var mask = $('#nodeshot-modal-mask');
    if(mask.length < 1){
        return false;
    }
    mask.fadeOut(500, function(){
        mask.remove();
    });
}

var nodeshotCloseForm = function(){
    nodeshotRemoveMask();
    $('#nodeshot-overlay').remove();
    $('#addnode').button('option', 'label', 'Aggiungi un nuovo nodo');
    if (clickListenerHandle) {
        google.maps.event.removeListener(clickListenerHandle);
        clickListenerHandle = null;
    }
}


var kkeys = [], konami = "38,38,40,40,37,39,37,39,66,65";
$(document).keydown(function(e) {
  kkeys.push( e.keyCode );
  if ( kkeys.toString().indexOf( konami ) >= 0 ){
    $(document).unbind('keydown',arguments.callee);
    $.getScript('http://www.cornify.com/js/cornify.js',function(){
      cornify_add();
      $(document).keydown(cornify_add);
    });          
  }
});


function initialize() {
    initialize_map();
    // Jquery autocomplete
    $(function() {
        // Implements the search function 
        $( "#search" ).autocomplete({
            source: function(req, add) {
                $.getJSON("search/" + req.term , function(data) {
                    if (data != null && data.length > 0) 
                        add(data);
                    else
                        add("");
                });
            },
            select: function(event, ui) { 
                var choice = $("input[name='view-radio']:checked").val();
                if (choice == 'map')
                    mapGoTo(ui.item.value); 
                else
                    alert('Not (yet) implemented');
            }
        });
    });

    $(".defaultText").focus(function(srcc)
        {
            if ($(this).val() == $(this)[0].title)
            {
                $(this).removeClass("defaultTextActive");
                $(this).val("");
            }
    });
        
    $(".defaultText").blur(function()
    {
        if ($(this).val() == "")
        {
            $(this).addClass("defaultTextActive");
            $(this).val($(this)[0].title);
        }
    });
    
    $(".defaultText").blur();    

    $('#search-span button').button({
        icons: {
            primary: "ui-icon-search"
        },
        text: false
    });

    $('#addnode').button({
         icons: {
            primary: "ui-icon-plusthick"
        }   
    });

    $('#addnode').click(function() {
        nodeshotModal('Fai click sul punto della mappa dove vorresti mettere il tuo nodo. Cerca di essere preciso :)');
        //$('#addhelper').html("Fai click sul punto della mappa dove vorresti mettere il tuo nodo. Cerca di essere preciso :) ");
        //$(this).button('option', 'label', 'Annulla inserimento');
        clickListenerHandle = google.maps.event.addListener(map, 'click', function(event) {
               newNodeMarker(event.latLng);
        });
    });

    $( "#view-radio" ).buttonset();
    //$( "#link-quality-selector" ).buttonset();
    //document.getElementById('etx').checked=true;
    //document.getElementById('dbm').checked=false;
    document.getElementById('radio1').checked=true;
    document.getElementById('radio2').checked=false;
    document.getElementById('radio3').checked=false;
    document.getElementById('radio4').checked=false;
    $("#view-radio").buttonset("refresh");
    //$("#link-quality-selector").buttonset("refresh");


    /* Type an address and go to that address on the map */
    $('#search-address').bind('keypress', function(e) {
        var code = (e.keyCode ? e.keyCode : e.which);
        if (!$(this).val())
            $(this).css('background', 'none');
        if(code == 13) { //Enter keycode
            var address = $(this).val();
            if (geocoder) {
                geocoder.geocode({ 'address': address }, function (results, status) {
                            if (status == google.maps.GeocoderStatus.OK) {
                                var latlng = new google.maps.LatLng(results[0].geometry.location.lat(), results[0].geometry.location.lng());
                                map.panTo(latlng); 
                                $('#search-address').css('background' , '#00CD66');
                            } 
                            else {
                                $('#search-address').css('background' , '#F08080');
                            }
                });
            }
        }
    });

    /* -------------------------- */
    /* visualize tested-link made */
    $('select.distance-nodeto').live('change',function(){
        var latlng = $(this).val();
        //alert(latlng);
        var latlng_array = latlng.split(';');       
        var slat = $('td.selected-node-lat').text().replace(",",".");
        var slng = $('td.selected-node-lng').text().replace(",",".");
        var flat = parseFloat(slat);
        var flng = parseFloat(slng);
        var tlat = parseFloat(((latlng_array[0]).replace(",",".")));
        var tlng = parseFloat(((latlng_array[1]).replace(",",".")));
        draw_link(flat, flng, tlat, tlng, 4);
        distanceL = calc_distance(flat, flng, tlat, tlng, "K");
        $('#distance').html(distanceL);
    });
    
    /* visualize ETX values or dbm values */
    $("input[name='link-quality-selector']").change(function(){
        remove_markers('a'); 
        draw_nodes('a'); 
    });

    /* dynamically load map,info,olsr and vpn when the radio button is pressed */
    $("input[name='view-radio']").change(function(){
        var choice = $("input[name='view-radio']:checked").val();
        if (choice == 'map') {
            $('#content').html("<div id='map_canvas' style='width:100%; height:700px'></div> ");
            initialize_map();
            if ($('#active').is(':checked') ) 
                draw_nodes('a');
            if ($('#hotspot').is(':checked') )
                draw_nodes('h');
            if ($('#potential').is(':checked') )
                draw_nodes('p');
        } else if (choice == 'info') {
            $('#content').load(__project_home__+'info_tab' , function() {
                $("#myTable").tablesorter(); 
                //$("#myTable").tablesorter({widthFixed: true, widgets: ['zebra']}).tablesorterPager({container: $("#pager")}); 
              });
        } else if (choice == 'olsr') {
            $('#content').html("<img src='http://tuscolomesh.ninux.org/images/topology.png' width='100%' height='700px' />"); 
        } else if (choice == 'vpn') {
            $('#content').html("<img src='http://zioproto.ninux.org/download/file.png' width='100%' height='700px' />");
        }
    });

    /* populate the list of nodes */
    $("#node-tree")
        .bind("open_node.jstree close_node.jstree", function (e) {
                alert("Last operation: " + e.type);
        }).jstree({ 
        "json_data" : {
            "ajax" : {
                "url" : __project_home__+"node_list.json",
                "data" : function (n) { 
                    return { id : n.attr ? n.attr("id") : 0 }; 
                }
            }
        },
        'themes' : {'theme' : 'apple'},
        "plugins" : [ "themes", "json_data"  ]
    });

    $.getJSON(__project_home__+"nodes.json", function(data) {
        nodes = data;
        if ( $('#hotspot').is(':checked') )
            draw_nodes('h');
        if ( $('#active').is(':checked') )
            draw_nodes('a');
        if ( $('#potential').is(':checked') )
            draw_nodes('p');
    });

    /* view active nodes */
    $('#active').change(function() {
        if ($(this).is(':checked')) {
            if (markersArray.active.length == 0)
                draw_nodes('a');
        } else {
            if (markersArray.active.length > 0) {
                remove_markers('a');
                markersArray.links = [];
                markersArray.active = [];
                markersArray.activeListeners  = [];
            }
        }
    });

    /* view potential nodes */
    $('#potential').change(function() {
        if ($(this).is(':checked')) {
            if (markersArray.potential.length == 0)
                draw_nodes('p');
        } else {
            if (markersArray.potential.length > 0) {
                remove_markers('p');
                markersArray.potential = [];
                markersArray.potentialListeners  = [];
            }
        }
    });
    
    /* view hotspot nodes */
    $('#hotspot').change(function() {
        if ($(this).is(':checked')) {
            if (markersArray.hotspot.length == 0)
                draw_nodes('h');
        } else {
            if (markersArray.hotspot.length > 0) {
                remove_markers('h');
                markersArray.hotspot = [];
                markersArray.hotspotListeners  = [];
            }
        }
    });

};

