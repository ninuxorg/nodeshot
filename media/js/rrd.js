/* 
 * This file contains all the functions needed to visualize the RRD graphs of nodes 
 * through the rrdFlot library 
 * 
 */

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
    fname = nodeshot.global.root_url+'media/graphs/rrds/' + ip + '.rrd';
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
        $( "#node-info-box" ).attr('title', ip).dialog({ width: 650 , height: 550});
}
