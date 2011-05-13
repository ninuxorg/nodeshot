/*
 * RRD graphing libraries, based on Flot
 * Part of the javascriptRRD package
 * Copyright (c) 2010 Frank Wuerthwein, fkw@ucsd.edu
 *                    Igor Sfiligoi, isfiligoi@ucsd.edu
 *
 * Original repository: http://javascriptrrd.sourceforge.net/
 * 
 * MIT License [http://www.opensource.org/licenses/mit-license.php]
 *
 */

/*
 *
 * Flot is a javascript plotting library developed and maintained by
 * Ole Laursen [http://code.google.com/p/flot/]
 *
 */

/*
 * Local dependencies:
 *  rrdFlotSupport.py
 *
 * External dependencies:
 *  [Flot]/jquery.py
 *  [Flot]/jquery.flot.js
 *  [Flot]/jquery.flot.selection.js
 */

/* graph_options defaults (see Flot docs for details)
 * {
 *  legend: { position:"nw",noColumns:3},
 *  lines: { show:true },
 *  yaxis: { autoscaleMargin: 0.20}
 * }
 *
 * ds_graph_options is a dictionary of DS_name, 
 *   with each element being a graph_option
 *   The defaults for each element are
 *   {
 *     title: label  or ds_name     // this is what is displayed in the checkboxes
 *     checked: first_ds_in_list?   // boolean
 *     label: title or ds_name      // this is what is displayed in the legend
 *     color: ds_index              // see Flot docs for details
 *     lines: { show:true }         // see Flot docs for details
 *     yaxis: 1                     // can be 1 or 2
 *     stack: 'none'                // other options are 'positive' and 'negative'
 *   }
 */

function rrdFlot(html_id, rrd_file, graph_options, ds_graph_options) {
  this.html_id=html_id;
  this.rrd_file=rrd_file;
  this.graph_options=graph_options;
  if (ds_graph_options==null) {
    this.ds_graph_options=new Object(); // empty object, just not to be null
  } else {
    this.ds_graph_options=ds_graph_options;
  }
  this.selection_range=new rrdFlotSelection();

  this.createHTML();
  this.populateRes();
  this.populateDScb();
  this.drawFlotGraph()
}


// ===============================================
// Create the HTML tags needed to host the graphs
rrdFlot.prototype.createHTML = function() {
  var rf_this=this; // use obj inside other functions

  var base_el=document.getElementById(this.html_id);

  this.res_id=this.html_id+"_res";
  this.ds_cb_id=this.html_id+"_ds_cb";
  this.graph_id=this.html_id+"_graph";
  this.scale_id=this.html_id+"_scale";
  this.legend_sel_id=this.html_id+"_legend_sel";

  // First clean up anything in the element
  while (base_el.lastChild!=null) base_el.removeChild(base_el.lastChild);

  // Now create the layout
  var external_table=document.createElement("Table");

  // Header rwo: resulution select and DS selection title
  var rowHeader=external_table.insertRow(-1);
  var cellRes=rowHeader.insertCell(-1);
  cellRes.colSpan=3;
  cellRes.appendChild(document.createTextNode("Resolution:"));
  var forRes=document.createElement("Select");
  forRes.id=this.res_id;
  //forRes.onChange= this.callback_res_changed;
  forRes.onchange= function () {rf_this.callback_res_changed();};
  cellRes.appendChild(forRes);

  var cellDSTitle=rowHeader.insertCell(-1);
  cellDSTitle.appendChild(document.createTextNode("Select elements to plot:"));

  // Graph row: main graph and DS selection block
  var rowGraph=external_table.insertRow(-1);
  var cellGraph=rowGraph.insertCell(-1);
  cellGraph.colSpan=3;
  var elGraph=document.createElement("Div");
  elGraph.style.width="500px";
  elGraph.style.height="300px";
  elGraph.id=this.graph_id;
  cellGraph.appendChild(elGraph);

  var cellDScb=rowGraph.insertCell(-1);
  cellDScb.vAlign="top";
  var formDScb=document.createElement("Form");
  formDScb.id=this.ds_cb_id;
  formDScb.onchange= function () {rf_this.callback_ds_cb_changed();};
  cellDScb.appendChild(formDScb);

  // Scale row: scaled down selection graph
  var rowScale=external_table.insertRow(-1);

  var cellScaleLegend=rowScale.insertCell(-1);
  cellScaleLegend.vAlign="top";
  cellScaleLegend.appendChild(document.createTextNode("Legend:"));
  cellScaleLegend.appendChild(document.createElement('br'));
  var forScaleLegend=document.createElement("Select");
  forScaleLegend.id=this.legend_sel_id;
  forScaleLegend.appendChild(new Option("Top","nw"));
  forScaleLegend.appendChild(new Option("Bottom","sw"));
  forScaleLegend.appendChild(new Option("TopRight","ne"));
  forScaleLegend.appendChild(new Option("BottomRight","se"));
  forScaleLegend.appendChild(new Option("None","None"));
  forScaleLegend.onchange= function () {rf_this.callback_legend_changed();};
  cellScaleLegend.appendChild(forScaleLegend);

  var cellScale=rowScale.insertCell(-1);
  cellScale.align="right";
  var elScale=document.createElement("Div");
  elScale.style.width="250px";
  elScale.style.height="110px";
  elScale.id=this.scale_id;
  cellScale.appendChild(elScale);
  
  var cellScaleReset=rowScale.insertCell(-1);
  cellScaleReset.vAlign="top";
  cellScaleReset.appendChild(document.createTextNode(" "));
  cellScaleReset.appendChild(document.createElement('br'));
  var elScaleReset=document.createElement("input");
  elScaleReset.type = "button";
  elScaleReset.value = "Reset selection";
  elScaleReset.onclick = function () {rf_this.callback_scale_reset();}

  cellScaleReset.appendChild(elScaleReset);

  base_el.appendChild(external_table);
};

// ======================================
// Populate RRA and RD info
rrdFlot.prototype.populateRes = function() {
  var form_el=document.getElementById(this.res_id);

  // First clean up anything in the element
  while (form_el.lastChild!=null) form_el.removeChild(form_el.lastChild);

  // now populate with RRA info
  var nrRRAs=this.rrd_file.getNrRRAs();
  for (var i=0; i<nrRRAs; i++) {
    var rra=this.rrd_file.getRRAInfo(i);
    var step=rra.getStep();
    var rows=rra.getNrRows();
    var period=step*rows;
    var rra_label=rfs_format_time(step)+" ("+rfs_format_time(period)+" total)";
    form_el.appendChild(new Option(rra_label,i));
  }
};

rrdFlot.prototype.populateDScb = function() {
  var form_el=document.getElementById(this.ds_cb_id);

  // First clean up anything in the element
  while (form_el.lastChild!=null) form_el.removeChild(form_el.lastChild);

  // now populate with DS info
  var nrDSs=this.rrd_file.getNrDSs();
  for (var i=0; i<nrDSs; i++) {
    var ds=this.rrd_file.getDS(i);
    var name=ds.getName();
    var title=name;
    var checked=true; // (i==0); // only first checked by default
    if (this.ds_graph_options[name]!=null) {
      var dgo=this.ds_graph_options[name];
      if (dgo['title']!=null) {
	// if the user provided the title, use it
	title=dgo['title'];
      } else if (dgo['label']!=null) {
	// use label as a second choiceit
	title=dgo['label'];
      } // else leave the ds name
      if (dgo['checked']!=null) {
	// if the user provided the title, use it
	checked=dgo['checked'];
      }
    }

    var cb_el = document.createElement("input");
    cb_el.type = "checkbox";
    cb_el.name = "ds";
    cb_el.value = name;
    cb_el.checked = cb_el.defaultChecked = checked;
    form_el.appendChild(cb_el);
    form_el.appendChild(document.createTextNode(title));
    form_el.appendChild(document.createElement('br'));
  }
};

// ======================================
// 
rrdFlot.prototype.drawFlotGraph = function() {
  // Res contains the RRA idx
  var oSelect=document.getElementById(this.res_id);
  var rra_idx=Number(oSelect.options[oSelect.selectedIndex].value);

  // now get the list of selected DSs
  var ds_positive_stack_list=[];
  var ds_negative_stack_list=[];
  var ds_single_list=[];
  var ds_colors={};
  var oCB=document.getElementById(this.ds_cb_id);
  var nrDSs=oCB.ds.length;
  if (oCB.ds.length>0) {
    for (var i=0; i<oCB.ds.length; i++) {
      if (oCB.ds[i].checked==true) {
	var ds_name=oCB.ds[i].value;
	var ds_stack_type='none';
	if (this.ds_graph_options[ds_name]!=null) {
	  var dgo=this.ds_graph_options[ds_name];
	  if (dgo['stack']!=null) {
	    var ds_stack_type=dgo['stack'];
	  }
	}
	if (ds_stack_type=='positive') {
	  ds_positive_stack_list.push(ds_name);
	} else if (ds_stack_type=='negative') {
	  ds_negative_stack_list.push(ds_name);
	} else {
	  ds_single_list.push(ds_name);
	}
	ds_colors[ds_name]=i;
      }
    }
  } else { // single element is not treated as an array
    if (oCB.ds.checked==true) {
      // no sense trying to stack a single element
      var ds_name=oCB.ds.value;
      ds_single_list.push(ds_name);
      ds_colors[ds_name]=0;
    }
  }
  
  // then extract RRA data about those DSs
  var flot_obj=rrdRRAStackFlotObj(this.rrd_file,rra_idx,
				  ds_positive_stack_list,ds_negative_stack_list,ds_single_list);

  // fix the colors, based on the position in the RRD
  for (var i=0; i<flot_obj.data.length; i++) {
    var name=flot_obj.data[i].label; // at this point, label is the ds_name
    var color=ds_colors[name]; // default color as defined above
    if (this.ds_graph_options[name]!=null) {
      var dgo=this.ds_graph_options[name];
      if (dgo['color']!=null) {
	color=dgo['color'];
      }
      if (dgo['label']!=null) {
	// if the user provided the label, use it
	flot_obj.data[i].label=dgo['label'];
      } else  if (dgo['title']!=null) {
	// use title as a second choice 
	flot_obj.data[i].label=dgo['title'];
      } // else use the ds name
      if (dgo['lines']!=null) {
	// if the user provided the label, use it
	flot_obj.data[i].lines=dgo['lines'];
      }
      if (dgo['yaxis']!=null) {
	// if the user provided the label, use it
	flot_obj.data[i].yaxis=dgo['yaxis'];
      }
    }
    flot_obj.data[i].color=color;
  }

  // finally do the real plotting
  this.bindFlotGraph(flot_obj);
};

// ======================================
// Bind the graphs to the HTML tags
rrdFlot.prototype.bindFlotGraph = function(flot_obj) {
  var rf_this=this; // use obj inside other functions

  // Legend
  var oSelect=document.getElementById(this.legend_sel_id);
  var legend_id=oSelect.options[oSelect.selectedIndex].value;

  var graph_jq_id="#"+this.graph_id;
  var scale_jq_id="#"+this.scale_id;

  var graph_options = {
    legend: {show:false, position:"nw",noColumns:3},
    lines: {show:true},
    xaxis: { mode: "time" },
    yaxis: { autoscaleMargin: 0.20},
    selection: { mode: "x" },
  };

  if (legend_id=="None") {
    // do nothing
  } else {
    graph_options.legend.show=true;
    graph_options.legend.position=legend_id;
  }

  if (this.selection_range.isSet()) {
    var selection_range=this.selection_range.getFlotRanges();
    graph_options.xaxis.min=selection_range.xaxis.from;
    graph_options.xaxis.max=selection_range.xaxis.to;
  } else {
    graph_options.xaxis.min=flot_obj.min;
    graph_options.xaxis.max=flot_obj.max;
  }

  if (this.graph_options!=null) {
    if (this.graph_options.legend!=null) {
      if (this.graph_options.legend.position!=null) {
	graph_options.legend.position=this.graph_options.legend.position;
      }
      if (this.graph_options.legend.noColumns!=null) {
	graph_options.legend.noColumns=this.graph_options.legend.noColumns;
      }
    }
    if (this.graph_options.yaxis!=null) {
      if (this.graph_options.yaxis.autoscaleMargin!=null) {
	graph_options.yaxis.autoscaleMargin=this.graph_options.yaxis.autoscaleMargin;
      }
    }
    if (this.graph_options.lines!=null) {
      graph_options.lines=this.graph_options.lines;
    }
  }

  var scale_options = {
    legend: {show:false},
    lines: {show:true},
    xaxis: { mode: "time", min:flot_obj.min, max:flot_obj.max },
    selection: { mode: "x" },
  };
    
  var flot_data=flot_obj.data;

  var graph_data=this.selection_range.trim_flot_data(flot_data);
  var scale_data=flot_data;

  this.graph = $.plot($(graph_jq_id), graph_data, graph_options);
  this.scale = $.plot($(scale_jq_id), scale_data, scale_options);

  if (this.selection_range.isSet()) {
    this.scale.setSelection(this.selection_range.getFlotRanges(),true); //don't fire event, no need
  }

  // now connect the two    
  $(graph_jq_id).unbind("plotselected"); // but first remove old function
  $(graph_jq_id).bind("plotselected", function (event, ranges) {
      // do the zooming
      rf_this.selection_range.setFromFlotRanges(ranges);
      graph_options.xaxis.min=ranges.xaxis.from;
      graph_options.xaxis.max=ranges.xaxis.to;
      rf_this.graph = $.plot($(graph_jq_id), rf_this.selection_range.trim_flot_data(flot_data), graph_options);
      
      // don't fire event on the scale to prevent eternal loop
      rf_this.scale.setSelection(ranges, true);
  });
   
  $(scale_jq_id).unbind("plotselected"); //same here 
  $(scale_jq_id).bind("plotselected", function (event, ranges) {
      rf_this.graph.setSelection(ranges);
  });

  // only the scale has a selection
  // so when that is cleared, redraw also the graph
  $(scale_jq_id).bind("plotunselected", function() {
      rf_this.selection_range.reset();
      graph_options.xaxis.min=flot_obj.min;
      graph_options.xaxis.max=flot_obj.max;
      rf_this.graph = $.plot($(graph_jq_id), rf_this.selection_range.trim_flot_data(flot_data), graph_options);
  });
};

// callback functions that are called when one of the selections changes
rrdFlot.prototype.callback_res_changed = function() {
  this.drawFlotGraph();
};

rrdFlot.prototype.callback_ds_cb_changed = function() {
  this.drawFlotGraph();
};

rrdFlot.prototype.callback_scale_reset = function() {
  this.scale.clearSelection();
};

rrdFlot.prototype.callback_legend_changed = function() {
  this.drawFlotGraph();
};

