/*
 * Filter classes for rrdFile
 * They implement the same interface, but changing the content
 * 
 * Part of the javascriptRRD package
 * Copyright (c) 2009 Frank Wuerthwein, fkw@ucsd.edu
 *
 * Original repository: http://javascriptrrd.sourceforge.net/
 * 
 * MIT License [http://www.opensource.org/licenses/mit-license.php]
 *
 */

/*
 * All filter classes must implement the following interface:
 *     getMinStep()
 *     getLastUpdate()
 *     getNrRRAs()
 *     getRRAInfo(rra_idx)
 *     getFilterRRA(rra_idx)
 *     getName()
 *
 * Where getFilterRRA returns an object implementing the following interface:
 *     getIdx()
 *     getNrRows()
 *     getStep()
 *     getCFName()
 *     getEl(row_idx)
 *     getElFast(row_idx)
 *
 */


// ================================================================
// Filter out a subset of DSs (identified either by idx or by name)

function RRDRRAFilterDS(rrd_rra,ds_list) {
  this.rrd_rra=rrd_rra;
  this.ds_list=ds_list;
}
RRDRRAFilterDS.prototype.getIdx = function() {return this.rrd_rra.getIdx();}
RRDRRAFilterDS.prototype.getNrRows = function() {return this.rrd_rra.getNrRows();}
RRDRRAFilterDS.prototype.getNrDSs = function() {return this.ds_list.length;}
RRDRRAFilterDS.prototype.getStep = function() {return this.rrd_rra.getStep();}
RRDRRAFilterDS.prototype.getCFName = function() {return this.rrd_rra.getCFName();}
RRDRRAFilterDS.prototype.getEl = function(row_idx,ds_idx) {
  if ((ds_idx>=0) && (ds_idx<this.ds_list.length)) {
    var real_ds_idx=this.ds_list[ds_idx].real_ds_idx;
    return this.rrd_rra.getEl(row_idx,real_ds_idx);
  } else {
    throw RangeError("DS idx ("+ ds_idx +") out of range [0-" + this.ds_list.length +").");
  }	
}
RRDRRAFilterDS.prototype.getElFast = function(row_idx,ds_idx) {
  if ((ds_idx>=0) && (ds_idx<this.ds_list.length)) {
    var real_ds_idx=this.ds_list[ds_idx].real_ds_idx;
    return this.rrd_rra.getElFast(row_idx,real_ds_idx);
  } else {
    throw RangeError("DS idx ("+ ds_idx +") out of range [0-" + this.ds_list.length +").");
  }	
}


// --------------------------------------------------
function RRDFilterDS(rrd_file,ds_id_list) {
  this.rrd_file=rrd_file;
  this.ds_list=[];
  for (var i=0; i<ds_id_list.length; i++) {
    var org_ds=rrd_file.getDS(ds_id_list[i]);
    // must create a new copy, as the index has changed
    var new_ds=new RRDDS(org_ds.rrd_data,org_ds.rrd_data_idx,i);
    // then extend it to include the real RRD index
    new_ds.real_ds_idx=org_ds.my_idx;

    this.ds_list.push(new_ds);
  }
}
RRDFilterDS.prototype.getMinSteps = function() {return this.rrd_file.getMinSteps();}
RRDFilterDS.prototype.getLastUpdate = function() {return this.rrd_file.getLastUpdate();}

RRDFilterDS.prototype.getNrDSs = function() {return this.ds_list.length;}
RRDFilterDS.prototype.getDSNames = function() {
  var ds_names=[];
  for (var i=0; i<this.ds_list.length; i++) {
    ds_names.push(ds_list[i].getName());
  }
  return ds_names;
}
RRDFilterDS.prototype.getDS = function(id) {
  if (typeof id == "number") {
    return this.getDSbyIdx(id);
  } else {
    return this.getDSbyName(id);
  }
}

// INTERNAL: Do not call directly
RRDFilterDS.prototype.getDSbyIdx = function(idx) {
  if ((idx>=0) && (idx<this.ds_list.length)) {
    return this.ds_list[idx];
  } else {
    throw RangeError("DS idx ("+ idx +") out of range [0-" + this.ds_list.length +").");
  }	
}

// INTERNAL: Do not call directly
RRDFilterDS.prototype.getDSbyName = function(name) {
  for (var idx=0; idx<this.ds_list.length; idx++) {
    var ds=this.ds_list[idx];
    var ds_name=ds.getName()
    if (ds_name==name)
      return ds;
  }
  throw RangeError("DS name "+ name +" unknown.");
}

RRDFilterDS.prototype.getNrRRAs = function() {return this.rrd_file.getNrRRAs();}
RRDFilterDS.prototype.getRRAInfo = function(idx) {return this.rrd_file.getRRAInfo(idx);}
RRDFilterDS.prototype.getRRA = function(idx) {return new RRDRRAFilterDS(this.rrd_file.getRRA(idx),this.ds_list);}

// ================================================================
// Filter out by using a user provided filter object
// The object must implement the following interface
//   getName()               - Symbolic name give to this function
//   getDSName()             - list of DSs used in computing the result (names or indexes)
//   computeResult(val_list) - val_list contains the values of the requested DSs (in the same order) 

// Example class that implements the interface:
//   function sumDS(ds1,ds2) {
//     this.getName = function() {return ds1+"+"+ds2;}
//     this.getDSNames = function() {return [ds1,ds2];}
//     this.computeResult = function(val_list) {return val_list[0]+val_list[1];}
//   }

function RRDDSFilterOp(rrd_file,op_obj,my_idx) {
  this.rrd_file=rrd_file;
  this.op_obj=op_obj;
  this.my_idx=my_idx;
  var ds_names=op_obj.getDSNames();
  var ds_idx_list=[];
  for (var i=0; i<ds_names.length; i++) {
    ds_idx_list.push(rrd_file.getDS(ds_names[i]).getIdx());
  }
  this.ds_idx_list=ds_idx_list;
}
RRDDSFilterOp.prototype.getIdx = function() {return this.my_idx;}
RRDDSFilterOp.prototype.getName = function() {return this.op_obj.getName();}

RRDDSFilterOp.prototype.getType = function() {return "function";}
RRDDSFilterOp.prototype.getMin = function() {return undefined;}
RRDDSFilterOp.prototype.getMax = function() {return undefined;}

// These are new to RRDDSFilterOp
RRDDSFilterOp.prototype.getRealDSList = function() { return this.ds_idx_list;}
RRDDSFilterOp.prototype.computeResult = function(val_list) {return this.op_obj.computeResult(val_list);}

// --------------------------------------------------
function RRDRRAFilterOp(rrd_rra,ds_list) {
  this.rrd_rra=rrd_rra;
  this.ds_list=ds_list;
}
RRDRRAFilterOp.prototype.getIdx = function() {return this.rrd_rra.getIdx();}
RRDRRAFilterOp.prototype.getNrRows = function() {return this.rrd_rra.getNrRows();}
RRDRRAFilterOp.prototype.getNrDSs = function() {return this.ds_list.length;}
RRDRRAFilterOp.prototype.getStep = function() {return this.rrd_rra.getStep();}
RRDRRAFilterOp.prototype.getCFName = function() {return this.rrd_rra.getCFName();}
RRDRRAFilterOp.prototype.getEl = function(row_idx,ds_idx) {
  if ((ds_idx>=0) && (ds_idx<this.ds_list.length)) {
    var ds_idx_list=this.ds_list[ds_idx].getRealDSList();
    var val_list=[];
    for (var i=0; i<ds_idx_list.length; i++) {
      val_list.push(this.rrd_rra.getEl(row_idx,ds_idx_list[i]));
    }
    return this.ds_list[ds_idx].computeResult(val_list);
  } else {
    throw RangeError("DS idx ("+ ds_idx +") out of range [0-" + this.ds_list.length +").");
  }	
}
RRDRRAFilterOp.prototype.getElFast = function(row_idx,ds_idx) {
  if ((ds_idx>=0) && (ds_idx<this.ds_list.length)) {
    var ds_idx_list=this.ds_list[ds_idx].getRealDSList();
    var val_list=[];
    for (var i=0; i<ds_idx_list.length; i++) {
      val_list.push(this.rrd_rra.getEl(row_idx,ds_idx_list[i]));
    }
    return this.ds_list[ds_idx].computeResult(val_list);
  } else {
    throw RangeError("DS idx ("+ ds_idx +") out of range [0-" + this.ds_list.length +").");
  }	
}

// --------------------------------------------------
function RRDFilterOp(rrd_file,op_obj_list) {
  this.rrd_file=rrd_file;
  this.ds_list=[];
  for (var i=0; i<op_obj_list.length; i++) {
    this.ds_list.push(new RRDDSFilterOp(rrd_file,op_obj_list[i],i));
  }
}
RRDFilterOp.prototype.getMinSteps = function() {return this.rrd_file.getMinSteps();}
RRDFilterOp.prototype.getLastUpdate = function() {return this.rrd_file.getLastUpdate();}

RRDFilterOp.prototype.getNrDSs = function() {return this.ds_list.length;}
RRDFilterOp.prototype.getDSNames = function() {
  var ds_names=[];
  for (var i=0; i<this.ds_list.length; i++) {
    ds_names.push(ds_list[i].getName());
  }
  return ds_names;
}
RRDFilterOp.prototype.getDS = function(id) {
  if (typeof id == "number") {
    return this.getDSbyIdx(id);
  } else {
    return this.getDSbyName(id);
  }
}

// INTERNAL: Do not call directly
RRDFilterOp.prototype.getDSbyIdx = function(idx) {
  if ((idx>=0) && (idx<this.ds_list.length)) {
    return this.ds_list[idx];
  } else {
    throw RangeError("DS idx ("+ idx +") out of range [0-" + this.ds_list.length +").");
  }	
}

// INTERNAL: Do not call directly
RRDFilterOp.prototype.getDSbyName = function(name) {
  for (var idx=0; idx<this.ds_list.length; idx++) {
    var ds=this.ds_list[idx];
    var ds_name=ds.getName()
    if (ds_name==name)
      return ds;
  }
  throw RangeError("DS name "+ name +" unknown.");
}

RRDFilterOp.prototype.getNrRRAs = function() {return this.rrd_file.getNrRRAs();}
RRDFilterOp.prototype.getRRAInfo = function(idx) {return this.rrd_file.getRRAInfo(idx);}
RRDFilterOp.prototype.getRRA = function(idx) {return new RRDRRAFilterOp(this.rrd_file.getRRA(idx),this.ds_list);}

