var nodes = [];
var map;
var geocoder;
var markersArray = {'active' : [], 'potential': [], 'activeListeners': [], 'potentialListeners': [], 'links': [] };
var newMarker;
var newMarkerListenerHandle;
var clickListenerHandle;
var infoWindow = new google.maps.InfoWindow;

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
    } else if (nodeStatus == 'p' &&  ! $('#potential').is(':checked') ) {
        $('#potential').attr('checked', true);
        draw_nodes('p');
    }
    if (nodeStatus == 'a')
        marray = markersArray.active;
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
        map.setZoom(15);
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
                  });
        var contentString = '<div id="info-content">Mi hai posizionato bene? </div> '+
            '<ul><li><a href="javascript:insertNodeInfo()">Si</a></li>'+
            '<li><a href="javascript:removeNewMarker()">No</a></li></ul>'

        var infowindow = new google.maps.InfoWindow({
            content: contentString
        });
        map.setCenter(location);
        infowindow.open(map,marker); 
        newMarkerListenerHandle = google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map,marker);
        });
        newMarker = marker;
}

function initialize_map() {
    var latlng = new google.maps.LatLng(41.90636538970964, 12.509307861328125);
    var myOptions = {
        zoom: 12,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"),
        myOptions);
    geocoder = new google.maps.Geocoder();
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
    else if (quality==2) 
        qualityColor =  '#ee0000' //Bad

    var link = new google.maps.Polyline({
        path: linkCoordinates,
        strokeColor: qualityColor,
        strokeOpacity: 0.4,
        strokeWeight: 8 
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
            draw_link(nodes.links[i].from_lat, nodes.links[i].from_lng, nodes.links[i].to_lat, nodes.links[i].to_lng, nodes.links[i].quality);
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
    } else if (type == 'p') {
        marray = markersArray.potential;
        larray = markersArray.potentialListeners;
    }
    for (i in marray) {
        google.maps.event.removeListener(larray[i]);
        marray[i].setMap(null);
    }


}

function initialize() {
    initialize_map();
    // Jquery autocomplete
    $(function() {
        var availableTags = [
            "08:00:0A:05:12:5F",
            "172.16.177.1",
            "172.16.177.2",
            "172.16.177.3",
            "172.16.177.4",
            "ActionScript",
            "AppleScript",
            "Asp",
            "BASIC",
            "C",
            "C++",
            "Clojure",
            "COBOL",
            "ColdFusion",
            "Erlang",
            "Fortran",
            "Groovy",
            "Haskell",
            "Java",
            "JavaScript",
            "Lisp",
            "Perl",
            "PHP",
            "Python",
            "Ruby",
            "Scala",
            "Scheme"
        ];
        $( "#search" ).autocomplete({
            source: availableTags
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
           var me = $('#addnode');
           if (me.hasClass('insert-mode')) {
               $('#addhelper').html(''); 
               $(this).button('option', 'label', 'Aggiungi un nuovo nodo');
               removeNewMarker();
               if (clickListenerHandle) {
                    google.maps.event.removeListener(clickListenerHandle);
                    clickListenerHandle = null;
               }
           } else {
               $('#addhelper').html("Fai click sul punto della mappa dove vorresti mettere il tuo nodo. Cerca di essere preciso :) ");
               $(this).button('option', 'label', 'Annulla inserimento');
               clickListenerHandle = google.maps.event.addListener(map, 'click', function(event) {
                      newNodeMarker(event.latLng);
               });
           }
           me.toggleClass('insert-mode');
    });



    $( "#view-radio" ).buttonset();


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




    $("input[name='view-radio']").change(function(){
        var choice = $("input[name='view-radio']:checked").val();
        if (choice == 'map') {
            $('#content').html("<div id='map_canvas' style='width:100%; height:700px'></div> ");
            initialize_map();
            if ($('#active').is(':checked') ) 
                draw_nodes('a');
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


    $("#node-tree")
        .bind("open_node.jstree close_node.jstree", function (e) {
                alert("Last operation: " + e.type);
        }).jstree({ 
        "json_data" : {
            "ajax" : {
		// 04/06/2011 added __project_home__ to avoid errors when the project root doesn't coincide with the webserver root
                "url" : __project_home__+"node_list.json",
                "data" : function (n) { 
                    return { id : n.attr ? n.attr("id") : 0 }; 
                }
            }
        },
        'themes' : {'theme' : 'apple'},
        "plugins" : [ "themes", "json_data"  ]
    });
    console.log(__project_home__);
    // 04/06/2011 - added __project_home__
    $.getJSON(__project_home__+"nodes.json", function(data) {
        nodes = data;
        if ( $('#active').is(':checked') )
            draw_nodes('a');
        if ( $('#potential').is(':checked') )
            draw_nodes('p');
    });

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

};

// Remove the Javascript warning
//document.getElementById("infotable").deleteRow(0);

 // fname and rrd_data are the global variable used by all the functions below
// fname="/media/graphs/rrds/172.16.40.5.rrd";
fname = '';
rrd_data=undefined;

 // This function updates the Web Page with the data from the RRD archive header
 // when a new file is selected
function update_fname() {
    // Finally, update the file name and enable the update button
    var graph_opts={legend: { noColumns:2}};
    var ds_graph_opts={'IN':{ label: 'in' , color: "#ff8000", 
                                     lines: { show: true, fill: true, fillColor:"#ffff80"} },
                       'OUT':{ label: 'out', color: "#00c0c0", 
                                lines: { show: true, fill: true} },
                       };

    // the rrdFlot object creates and handles the graph
    var f=new rrdFlot("rrd-graph",rrd_data,graph_opts,ds_graph_opts);
}

// This is the callback function that,
// given a binary file object,
// verifies that it is a valid RRD archive
// and performs the update of the Web page
function update_fname_handler(bf, fname) {
    var i_rrd_data=undefined;
    try {
        var i_rrd_data=new RRDFile(bf);            
    } catch(err) {
        alert("File "+fname+" is not a valid RRD archive!");
    }
    if (i_rrd_data!=undefined) {
        rrd_data=i_rrd_data;
        update_fname();
    }
}

// this function is invoked when the RRD file name changes
function fname_update(ip) {
    fname = __project_home__+'/media/graphs/rrds/' + ip + '.rrd';
    try {
      FetchBinaryURLAsync(fname,update_fname_handler);
      return true;
    } catch (err) {
       alert("Failed loading "+fname+"\n"+err);
       return false;
    }
}

function load_rrd(ip) {
        // $('#table-wrapper').css('height', '10%');
        // $('#node-info-box').css('height', '90%');
        // $('#node-info-box').css('display', 'block');
        // $('#node-info-box').load('http://nodeshot.peertoport.com/generate_rrd?ip=' + ip );
        $( "#rrd-graph" ).empty();
        $( "#node-info-box" ).attr('title', ip);
        $( "#node-info-box" ).dialog({ width: 650 , height: 550});
        fname_update(ip);
<<<<<<< HEAD
        $( "#node-info-box" ).attr('title', ip).dialog({ width: 650 , height: 550});
}
=======
}


>>>>>>> dce1752cea0ca8c8569c77bd397a7ff42a8a5229
