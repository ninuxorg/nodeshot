// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};

// Converts numeric degrees to radians
if (typeof(Number.prototype.toRad) === "undefined") {
    Number.prototype.toRad = function() {
        return this * Math.PI / 180;
    }
}

// Converts to degrees
if (typeof(Number.prototype.toDeg) === "undefined") {
    Number.prototype.toDeg = function() {
        return this * Math.PI / 180;
    }
}

var nodeshot = {
    
    // here we'll store the nodes (retrieved with nodeshot.getNodes())
    nodes: [],
    
    // possible statuses
    status_choices: {
        a: 'active',
        h: 'hotspot',
        p: 'potential'
    },
    
    // here we'll store some urls
    url: {
        index: '',
        media: ''        
    },
    
    // cache for jquery autocomplete search
    searchCache: [],
    
    /*
     * nodeshot.init()
     * inits nodeshot
     */
    init: function(){
        nodeshot.getNodes(); 
        nodeshot.layout.cacheObjects();
        nodeshot.layout.initSideControl();        
        nodeshot.gmap.init();
        nodeshot.remember();               
        nodeshot.layout.initSearchAddress();
        nodeshot.layout.initMainSearch();
        nodeshot.layout.initAddNode();
        nodeshot.layout.initChoices()
        nodeshot.layout.initPotential();
        nodeshot.layout.initLinkQuality();
        nodeshot.easterEgg();
    }, // nodeshot.init()
    
    /*
     * nodeshot.getNodes()
     * retrieves nodes from url with json and populates nodeshot.nodes
     */
    getNodes: function(){
        $.getJSON(nodeshot.url.index+"nodes.json", function(data) {
            nodeshot.nodes = data;
        });
    }, // nodeshot.getNodes()
    
    /*
     * nodeshot.remember()
     * remembers configurations of the user (show potential nodes, link quality, sidebar, distances)
     */
    remember: function(){
        // remember potential nodes checkbox
        if($.cookie('nodeshot_potential_nodes')=='false'){
            nodeshot.layout.$potential[0].checked = false;
        }
        // remember link quality selection
        if($.cookie('nodeshot_link_quality')=='dbm'){
            // don't need to cache this object as this is the only time we need it
            $('#dbm')[0].checked = true;
        }
        // remember if sidebar is shown or not
        if($.cookie('nodeshot_sidebar')=='false'){
            nodeshot.layout.$hideSide.trigger('click');
        }
        // store the cookie for use outside this function
        nodeshot.distance.cookie = $.cookie('nodeshot_saved_distances');
        // remember saved distance links
        if(nodeshot.distance.cookie){
            nodeshot.distance.saved_links = JSON.parse(nodeshot.distance.cookie);
            if(typeof(nodeshot.distance.saved_links)=='object'){
                // upcount negative while loop is more performant on modern browsers
                len = nodeshot.distance.saved_links.length + 1; // add 1 otherwise we'll miss 1 cycle
                ilen = len - 1; // subtract for the same reason as before
                if(len > 0){
                    while(--len){
                        nodeshot.gmap.drawDistanceLink(nodeshot.distance.saved_links[ilen-len], 'saved');
                    }
                }
            }
        }
    }, // nodeshot.remember()
    
    /*
     * nodeshot.layout
     * DOM, css and animation stuff
     */
    layout:{
        
        /*
        * nodeshot.layout.cacheObjects()
        * caches some jquery objects
        */
        cacheObjects: function(){
            this.$body = $('body');
            this.$mask = $('#nodeshot-mask');
            this.$loading = $('#loading');
            this.$container = $('#container');
            this.$header = $('#header');
            this.$content = $('#content');
            this.$aside = $('#aside');            
            this.$nodeTreeContainer = $('#node-tree-container');
            this.$nodeTree = $('#node-tree');
            this.$hideSide = $('#hide-side');
            this.$search = $('#search');
            this.$addNode = $('#addnode');
            this.$choices = $('#choices');
            this.$potential = $('#potential');
            this.$linkQuality = $('#link-quality');
        }, // nodeshot.cacheObjects()
        
        /*
        * nodeshot.layout.setFullScreen()
        * adds a mask over the <body>
        */
        setFullScreen: function(){
            // cache window
            var $window = $(window);
            // not too narrow
            if($window.width() > 950){
                // set total width
                this.$container.width($window.width());
                // set header width:
                this.$header.width($window.width());
                // if side column is not hidden
                if(!nodeshot.layout.$aside.hidden){
                    // set content column width
                    this.$content.width($window.width()-295);
                    // set side column width
                    this.$aside.width('295');   
                }
                else{
                    // set content 100%
                    this.$content.width($window.width());
                }
            }
            if(this.$map){
                // set map canvas height
                this.$map.height($window.height()-this.$header.height());
            }
            else if(this.$infoWrapper){
                this.$infoWrapper.height($window.height()-this.$header.height());
            }
            // set nodeTreeContainer height if not too short
            var newTreeHeight = this.$container.height()-this.$header.height()-(this.$nodeTreeContainer.position()).top;
            if(newTreeHeight > 100){
                this.$nodeTreeContainer.height(newTreeHeight);
            }
        }, // nodeshot.setFullScreen()
        
        /*
        * nodeshot.layout.setElementDimensions()
        * set absolute positioning to HTML elements dinamically
        */
        setElementDimensions: function(){
            this.$header.css({
                position:'absolute',
                top: 0,
                left: 0
            });
            this.$content.css({
                position:'absolute',
                marginTop: this.$header.height(),
                left: 0
            });
            this.$aside.css({
                marginTop: this.$header.height()
            });
        }, // nodeshot.setElementDimensions()
        
        /*
        * nodeshot.layout.getCssInt(string:string)
        * gets a css value as integer without 'px', 'em' or '%';
        */
        getCssInt: function(string){
            if(string){
                string = string.replace('px', '');
                string = string.replace('em', '');
                string.replace('%', '')
                integer = parseInt(string);
            }
            else{
                integer = 0;
            }
            return integer;
        }, // nodeshot.getCssInt()
        
        /*
        * nodeshot.layout.horizontalCenter(obj:jQuery)
        * calculates absolute left distance to center an object horizontally to the window
        */
        horizontalCenter: function(obj){
            if(obj){
                var paddingLeft = this.getCssInt(obj.css('padding-left'));
                var paddingRight = this.getCssInt(obj.css('padding-right'));
                var borderLeft = this.getCssInt(obj.css('border-left-width'));
                var borderRight = this.getCssInt(obj.css('border-right-width'));
                width = obj.width() + paddingLeft + paddingRight + borderLeft + borderRight;
                return ($(window).width() - width) / 2;   
            }
        }, // nodeshot.horizontalCenter()
        
        /*
        * nodeshot.layout.verticalCenter(obj:jQuery)
        * calculates absolute top distance to center an object vertically to the window
        */
        verticalCenter: function(obj){
            if(obj){
                var paddingTop = this.getCssInt(obj.css('padding-top'));
                var paddingBottom = this.getCssInt(obj.css('padding-bottom'));
                var borderTop = this.getCssInt(obj.css('border-top-width'));
                var borderBottom = this.getCssInt(obj.css('border-bottom-width'));
                height = obj.height() + paddingTop + paddingBottom + borderTop + borderBottom;
                return ($(window).height() - height) / 2;
            }
        }, // nodeshot.verticalCenter()
        
        /*
        * nodeshot.layout.bindFocusBlue(obj:jQuery)
        * binds onfocus and onblur event to obj (should be an input text field)
        */
        bindFocusBlur: function(obj){
            obj.focus(function(src){
                if (obj.val() == obj[0].defaultValue){
                    obj.val('');
                }
            });                
            obj.blur(function(){
                if ($(this).val() == '')
                {
                    $(this).val(obj[0].defaultValue);
                }
            });
        }, // nodeshot.bindFocusBlur()
        
        /*
        * nodeshot.layout.initSearchAddress()
        * search an address on google maps
        */
        initSearchAddress: function(){
            // bind click event to link
            $('#search-address').click(function(e){
                // prevent default link behaviour
                e.preventDefault();
                // if any google.maps.infoWindow object is open
                if(nodeshot.gmap.infoWindow){
                    // close it
                    nodeshot.gmap.infoWindow.close()
                }
                nodeshot.overlay.showMask();
                var data = '<div id="nodeshot-overlay-inner" class="content narrower"><div id="gmap-search"><h3>'+i18n.SEARCH_ADDRESS+'</h3><p>'+i18n.SEARCH_HINT+'</p><p><input type="text" class="text" id="gmap-address" /><input class="button" type="submit" value="'+i18n.SEARCH+'" id="gmap-submit" /></p></div></div>';
                nodeshot.overlay.open(data, false, nodeshot.gmap.removeNewMarker);
                // cache input
                var input = $('#gmap-address');
                // focus to search box
                input.trigger('focus');
                
                // bind keyup of search field
                input.bind('keyup', function(e) {
                    var code = (e.keyCode ? e.keyCode : e.which);
                    // if pressing enter do search
                    if (code == 13 && input.val()!=''){
                        nodeshot.gmap.searchAddress(input.val(), input);
                    }
                    // if just typing
                    else{
                        // remove eventual error class
                        if(input.hasClass('error')){
                            input.removeClass('error');
                        }
                    }
                });
                // if submitting do search
                $('#gmap-submit').click(function(){
                    nodeshot.gmap.searchAddress(input.val(), input);
                });
            });
        }, // nodeshot.layout.initSearchAddress()
        
        /*
        * nodeshot.layout.initSideControl()
        * hide / show side column
        */
        initSideControl: function(){
            // append invisible show-column button
            this.$body.append('<a id="show-column"></a>');
            // cache it
            this.$showColumn = $('#show-column');
            // bind click event on hide-side
            this.$hideSide.click(function(e){
                e.preventDefault();
                // disable scrollbars
                nodeshot.layout.$body.css('overflow', 'hidden');
                // prepare column to be moved
                nodeshot.layout.$aside.css({
                    right: 0,
                    position: 'absolute'
                });
                // hide column with an animation
                nodeshot.layout.$aside.animate({right: -300},500,function(){
                    // be sure $aside is hidden
                    nodeshot.layout.$aside.hide();
                    nodeshot.layout.$aside.hidden = true;
                    nodeshot.layout.$showColumn.show(500);
                });
                // enlarge the content with an animation
                nodeshot.layout.$content.animate({width: nodeshot.layout.$header.width()},500);
                // reset dimensions and re-enable scrollbar with some delay
                setTimeout(function(){
                    nodeshot.layout.setFullScreen();
                    // re-enable scrollbar
                    nodeshot.layout.$body.css('overflow', 'auto');
                }, 600);
                // save cookie to remember this choice
                $.cookie('nodeshot_sidebar', 'false', { expires: 365, path: nodeshot.url.index });
            });
            this.$showColumn.css('opacity', 0.5).hover(
                // mouse-enter
                function(){
                    nodeshot.layout.$showColumn.fadeTo(250, 1);
                },
                // mouse-out
                function(){
                    nodeshot.layout.$showColumn.fadeTo(250, 0.5);
                }
            ).click(function(){
                // disable scrollbar
                nodeshot.layout.$body.css('overflow', 'hidden');
                // set side column width
                nodeshot.layout.$aside.show().animate({
                    right: 0
                }, function(){
                    nodeshot.layout.$aside.hidden = false;
                    nodeshot.layout.$aside.css('position', 'static');                    
                });
                // set content column width
                nodeshot.layout.$content.animate({
                    width: $(window).width()-295
                });
                // hide show button
                nodeshot.layout.$showColumn.hide(500);
                // reset dimensions and re-enable scrollbar with some delay
                setTimeout(function(){                    
                    nodeshot.layout.setFullScreen();
                    nodeshot.layout.$body.css('overflow', 'auto');
                },600);
                // save cookie
                $.cookie('nodeshot_sidebar', 'true', { expires: 365, path: nodeshot.url.index });
            });
        }, // nodeshot.layout.initSideControl()
        
        /*
        * nodeshot.layout.initMainSearch()
        * initialize jquery autocomplete for the main search (nodes, ip, ecc.)
        */
        initMainSearch: function(){
            this.bindFocusBlur(this.$search);
            this.$search.autocomplete({
                // minimum length of keyword to start querying the database
                minLength: 3,
                // where to take the values from
                source: function(request, response) {
                    // store term in a local var
                    var term = request.term;
                    // check if term has already requested before
                    if (term in nodeshot.searchCache) {
                        // if has been found return the term in the cache
                        response(nodeshot.searchCache[term]);
                        return;
                    }
                    // if term has not been found in the cache go ahead with a new request
                    lastXhr = $.getJSON(nodeshot.url.index+'search/'+request.term+'/', function(data, status, xhr) {
                        // cache the term                        
                        if (xhr === lastXhr && data != null && data.length > 0){
                            nodeshot.searchCache[term] = data;
                            response(data);
                        }
                        else{
                            nodeshot.searchCache[term] = '';
                            response('');
                        }
                    });
                },
                // when an item  in the menu is clicked
                select: function(e, ui) {
                    var choice = nodeshot.layout.$choices.find('input:checked').val();
                    if (choice == 'map'){
                        // go to point on map
                        /*  this might be tricky to understand...
                                nodeshot.status_choices[ui.items.status]
                            means just 'active', 'hotspot' or 'potential'.
                            assuming it means 'active'
                                nodeshot.nodes[nodeshot.status_choices[ui.items.status]].nodename
                            would be the same as
                                nodeshot.nodes['active'].nodename
                            which is the same as
                                nodeshot.nodes.active.nodename
                        */
                        nodeshot.gmap.goToNode(nodeshot.nodes[nodeshot.status_choices[ui.item.status]][ui.item.value]);
                    }
                    else if(choice == 'info'){
                        nodeshot.infoTab.scrollTo(ui.item.slug);
                    }
                    else{
                        return false;
                    }
                    // put label on input
                    $(this).val(ui.item.label);
                    // return false to avoid default autocomplete plugin behaviour
                    return false;
                },
                // when an item in the menu is selected / focused
                focus: function(e, ui){
                    // put label on input
                    $(this).val(ui.item.label);
                    // return false to avoid default autocomplete plugin behaviour
                    return false;
                }
            });
        }, // nodeshot.layout.initMainSearch()
        
        /*
        * nodeshot.layout.initAddNode()
        * initialize add node button
        */
        initAddNode: function(){
            this.$addNode.click(function(e) {
                nodeshot.dialog.open(i18n.ADDNODE_DIALOG);
                nodeshot.gmap.clickListener = google.maps.event.addListener(nodeshot.gmap.map, 'click', function(e) {
                    nodeshot.gmap.newNodeMarker(e.latLng);
                });
            });
        }, // nodeshot.layout.initAddNode()
        
        /*
        * nodeshot.layout.initAddNode()
        * initialize buttonset to dynamically load map, info, olsr or vpn when the radio button is pressed
        */
        initChoices: function(){
            // init jquery ui buttonset
            this.$choices.buttonset();
            // default settings
            document.getElementById('radio1').checked=true;
            document.getElementById('radio2').checked=false;
            if(document.getElementById('radio3')){
                document.getElementById('radio3').checked=false;    
            }
            if(document.getElementById('radio4')){
                document.getElementById('radio4').checked=false;
            }
            this.$choices.buttonset('refresh');
            // bind change event
            this.$choices.find('input').change(function(){
                var choice = this.value;
                // if unloading map
                if(choice != 'map'){
                    if(!nodeshot.layout.$aside.maponly){
                        // fadeOut some functionalities that work for the map tab only
                        nodeshot.layout.$aside.find('#addnode, .maponly').fadeOut(500);
                        nodeshot.layout.$aside.maponly = true;
                    }
                }
                // if switching back to map
                if (choice == 'map') {
                    // if controls are hidden
                    if(nodeshot.layout.$aside.maponly){
                        // fadeOut some functionalities that work for the map tab only
                        nodeshot.layout.$aside.find('#addnode, .maponly').fadeIn(500);
                        delete nodeshot.layout.$aside.maponly;
                    }
                    // unload infoTab if necessary
                    if(nodeshot.layout.$infoTable){
                        nodeshot.infoTab.unload();
                    }
                    nodeshot.overlay.showMask(0.7);
                    nodeshot.overlay.showLoading();
                    nodeshot.layout.$content.html('<div id="map_canvas"></div><div id="side-links"></div>');
                    nodeshot.gmap.init();
                    nodeshot.remember();
                    nodeshot.layout.setFullScreen();
                    nodeshot.overlay.hideLoading();
                    nodeshot.overlay.hideMask();
                // if switching to info
                } else if (choice == 'info') {
                    // unload gmap if necessary
                    if(nodeshot.layout.$map){
                        nodeshot.gmap.unload();   
                    }
                    nodeshot.overlay.showMask(0.7);
                    nodeshot.overlay.showLoading();
                    nodeshot.layout.$content.load(nodeshot.url.index+'overview/' , function() {
                        nodeshot.infoTab.init();
                        nodeshot.layout.setFullScreen();
                        nodeshot.overlay.hideMask();
                        nodeshot.overlay.hideLoading();
                    });
                }
                // if switching to one of the other two possible buttons
                else if (choice == 'tab3' || choice == 'tab4') {
                    // unload gmap and infotable if necessary                
                    nodeshot.overlay.showMask(0.7);
                    nodeshot.overlay.showLoading();
                    if(nodeshot.layout.$map){
                        nodeshot.gmap.unload();   
                    }
                    if(nodeshot.layout.$infoTable){
                        nodeshot.infoTab.unload();
                    }
                    nodeshot.layout.$content.load(nodeshot.url.index+choice+'/', function(){
                        nodeshot.layout.setFullScreen();
                        nodeshot.overlay.hideMask();
                        nodeshot.overlay.hideLoading();
                    });
                }
            });
        }, // nodeshot.layout.initChoices()
        
        /*
        * nodeshot.layout.initLinkQuality()
        * dispaly link color depending on ETX values or dbm values
        */
        initLinkQuality: function(){
            // bind change event to the radios
            nodeshot.layout.$linkQuality.find('input').change(function(){
                // set cookie so we can remember this setting
                $.cookie('nodeshot_link_quality', this.id, { expires: 365, path: nodeshot.url.index });
                // remove links
                nodeshot.gmap.removeMarkers('active');
                // new links
                nodeshot.gmap.drawNodes('active'); 
            });
        }, // nodeshot.layout.initLinkQuality()
        
        /*
        * nodeshot.layout.initPotential()
        * initializes functionality of "show potential nodes" checkbox
        */
        initPotential: function(){
            // bind change event to the checkbox
            nodeshot.layout.$potential.change(function() {
                // if is being checked show potential nodes
                if (this.checked) {
                    // set cookie so that we can remember this setting
                    $.cookie('nodeshot_potential_nodes', 'true', { expires: 365, path: nodeshot.url.index });
                    nodeshot.gmap.drawNodes(nodeshot.status_choices.p);
                }
                // if is being unchecked remove potential nodes
                else {
                    // set cookie so that we can remember this setting
                    $.cookie('nodeshot_potential_nodes', 'false', { expires: 365, path: nodeshot.url.index });
                    nodeshot.gmap.removeMarkers(nodeshot.status_choices.p);
                }
            });
        }, // nodeshot.layout.initPotential()
        
        /*
        * nodeshot.layout.initNodeTree()
        * initializes jstree plugin
        * this method is called at the end of media/js/compressed/jquery.jstree.js
        */
        initNodeTree: function(){
            this.$nodeTree.jstree({
                'json_data' : {
                    'ajax' : {
                        // take stuff from the following url
                        'url' : nodeshot.url.index+'jstree.json',
                        // i wonder you don't understand this. Not me either. Who wrote it didn't bother to comment
                        'data' : function (n) {
                            return { id : n.attr ? n.attr('id') : 0 } 
                        }
                    }
                },
                'themes' : {'theme' : 'classic'},
                'plugins' : [ 'themes', 'json_data' ]
            });
        } // nodeshot.layout.initNodeTree()
    },
    
    /*
     * nodeshot.overlay
     * Overlay, Mask, Modal message, Loading gif
     */
    overlay: {
        
        /*
        * nodeshot.overlay.showMask(opacity:float [, closeOnClick:boolean])
        * adds a mask over the <body>
        */
        showMask: function(opacity, closeOnClick){
            // do not add more than one mask
            //if(document.getElementById('nodeshot-mask') != null){
            //    return false;
            //}
            // if opacity is not specified
            if(!opacity){
                // set default value
                opacity = 0.5
            }
            // initially not visible, but fades in
            var mask = nodeshot.layout.$mask;
            mask.css({
                opacity: 0,
                display: 'block'
            }).animate({
                opacity: opacity
            }, 500);
            // if closeOnClick == true bind click event that closes javascript stuff
            if(closeOnClick){
                mask.click(function(e){
                    nodeshot.overlay.hideMask();
                    // if dialog is open close it
                    if(nodeshot.layout.$dialog){
                        nodeshot.dialog.close();
                    }
                })
            }
        }, // nodeshot.overlay.showMask()
        
        /*
        * nodeshot.overlay.hideMask()
        * rermoves the mask
        */
        hideMask: function(){
            nodeshot.layout.$mask.fadeOut(500);
        }, // nodeshot.overlay.hideMask()
        
        /*
        * nodeshot.overlay.showLoading()
        * shows hidden loading gif appended previously
        */
        showLoading: function(){
            nodeshot.layout.$loading.show();
        }, // nodeshot.overlay.showLoading()
        
        /*
        * nodeshot.overlay.hideLoading()
        * hides Loading gif
        */
        hideLoading: function(){
            nodeshot.layout.$loading.hide();
        }, // nodeshot.overlay.hideLoading()
        
        /*
        * nodeshot.overlay.open(data:string [, closeOnClick: boolean])
        * opens overlay with data and positions to the center of the window
        */
        open: function(data, closeOnClick){
            this.hideLoading();
            // check if overlay is not already open
            if(nodeshot.layout.$overlay){
                nodeshot.layout.$overlay.remove();
            }
            nodeshot.layout.$body.append('<div id="nodeshot-overlay"></div>');   
            // cache jquery object
            nodeshot.layout.$overlay = $('#nodeshot-overlay');
            // innerHTML
            nodeshot.layout.$overlay.html(data);
            // cache inner object
            nodeshot.layout.$overlayInner = $('#nodeshot-overlay-inner');
            // close button
            this.initClose();
            // center overlay to window
            this.centerVertically();
            // update layout dimensions
            nodeshot.layout.setFullScreen();
            // if closeOnClick bind click event with a function that closes the overlay
            if(closeOnClick){
                nodeshot.layout.$overlay.click(function(e){
                    nodeshot.overlay.close();
                });
                nodeshot.layout.$overlayInner.click(function(){ return false });
            }
        }, // nodeshot.overlay.open()
        
        /*
        * nodeshot.overlay.initClose()
        * insert close button to overlay
        */
        initClose: function(){
            // insert close button to overlay
            nodeshot.layout.$overlayInner.prepend('<a class="close"></a>');
            // bind onclick event to close button
            nodeshot.layout.$overlayInner.find('.close').click(function(){
                nodeshot.overlay.close();
            });
        }, // nodeshot.overlay.initClose()
        
        /*
        * nodeshot.overlay.centerVertically(animate:boolean [, duration:int])
        * center the overlay vertically
        * if animate is true the overlay will move to the center with an animation of the specified duration
        */
        centerVertically: function(animate, duration){
            // cache calculation
            var margin = nodeshot.layout.verticalCenter(nodeshot.layout.$overlayInner);
            // if margin is negative set to 10            
            if(margin<0){ margin = 10 }
            // animate if specified
            if(animate){
                nodeshot.layout.$overlayInner.animate({'margin-top': margin}, duration);
            }
            else{
                nodeshot.layout.$overlayInner.css('margin-top', margin);
            }
        }, // nodeshot.overlay.centerVertically()
        
        /*
        * nodeshot.overlay.bindCancelButton()
        * binds actions to the cancel button of an overlay
        */
        bindCancelButton: function(){
            $('#cancel').click(function(){
                nodeshot.overlay.close();
            });
        }, // nodeshot.overlay.bindCancelButton()
        
        /*
        * nodeshot.overlay.bindSubmitForm(action:function)
        * binds actions to the submit event of an overlay
        */
        bindSubmitForm: function(action){
            $('#nodeshot-form').submit(function(e){
                // cache current form
                form = $(this);
                e.preventDefault();
                // avoid duplicate emails by setting/checking sending property
                if(!nodeshot.sending){
                    // pass form to action
                    action(form);
                    // set sending to true to avoid duplicate submits
                    nodeshot.sending = true;
                }
            });
        }, // nodeshot.overlay.bindSubmitForm()
        
        /*
        * nodeshot.overlay.close()
        * binds actions to the submit event of an overlay
        */
        close: function(){
            nodeshot.overlay.hideMask();
            nodeshot.layout.$overlay.remove();
            nodeshot.layout.$overlay = false;
            nodeshot.layout.$overlayInner = false;
            // reset dimensions
            nodeshot.layout.setFullScreen();
            // remove click listener from add new node
            if (nodeshot.gmap.clickListener) {
                google.maps.event.removeListener(nodeshot.gmap.clickListener);
                nodeshot.gmap.clickListener = null;
            }
            // delete any address marker
            if(nodeshot.gmap.addressMarker){
                nodeshot.gmap.removeAddressMarker();                
            }
        } // nodeshot.overlay.close()
        
    }, // nodeshot.overlay
    
    /*
    * nodeshot.dialog
    * handles messages to the user
    */
    dialog: {
        
        /*
        * nodeshot.dialog.open(message:string [, callback:function])
        * opens a dialog
        */
        open: function(message, callback){
            // add HTML elements
            $('body').append('<div id="nodeshot-modal"><div id="nodeshot-modal-message">'+message+'</div><a class="button green" id="nodeshot-modal-close">'+i18n.OK+'</a></div>');
            // cache jquery object
            nodeshot.layout.$dialog = $('#nodeshot-modal');
            // add mask after $container has been cached
            nodeshot.overlay.showMask(0.5, true);
            // set to the center of the window
            nodeshot.layout.$dialog.css({
                opacity: 0,
                display: 'block',
                left: nodeshot.layout.horizontalCenter(nodeshot.layout.$dialog),
                top: nodeshot.layout.verticalCenter(nodeshot.layout.$dialog)
            }).animate({
                // fade in
                opacity: 1
            }, 500);
            // bind key press event with some delay to avoid holding enter and not seeing the dialog for enough time
            setTimeout(function(){
                nodeshot.layout.$body.bind('keyup', function(e) {
                    var code = (e.keyCode ? e.keyCode : e.which);
                    // if pressing ENTER or ESC
                    if (code == 13 || code == 27){
                        nodeshot.dialog.close(callback);
                    }
                });
            }, 500);
            
            // bind close event
            $('#nodeshot-modal-close').click(function(){
                nodeshot.dialog.close(callback);
            });
        }, // nodeshot.dialog.open()
        
        /*
        * nodeshot.dialog.close([callback: function])
        */
        close: function(callback){
            if(nodeshot.layout.$dialog){
                // fade out and remove
                nodeshot.layout.$dialog.fadeOut(500, function(){
                    nodeshot.layout.$dialog.remove();
                    nodeshot.layout.$dialog = false;
                });
            }
            nodeshot.overlay.hideMask();
            // execute callback if any
            if(callback){
                callback();
            }
            // unbind keyup event
            nodeshot.layout.$body.unbind('keyup');
        } // nodeshot.dialog.close()
        
    }, // nodeshot.dialog
    
    /*
     * nodeshot.contact
     * Contact node stuff
     */
    contact: {
        
        /*
        * nodeshot.contact.init(url:string)
        * opens an overlay with the form to contact a node and binds the submit and cancel buttons
        */
        init: function(url){
            nodeshot.overlay.showMask(0.7);
            nodeshot.overlay.showLoading();
            // ajax get
            $.get(url, function(data) {
                nodeshot.overlay.hideLoading();
                nodeshot.overlay.open(data)
                // remember: we are not using $.live() for performance reasons so we need to rebind events
                nodeshot.overlay.bindCancelButton();
                nodeshot.overlay.bindSubmitForm(function(form){
                    nodeshot.contact.submit(url, form);
                });
            });
        }, // nodeshot.contact.init()
        
        /*
        * nodeshot.contact.submit(url:string, form:jQuery)
        * submits the form asynchronously and returns the result
        */
        submit: function(url, form){
            nodeshot.overlay.showLoading();
            // block the form by raising mask z-index and decreasing overlay z-index
            $('#nodeshot-mask').css({
                zIndex: 11,
                opacity: 0.7
            });
            nodeshot.layout.$overlay.css('z-index', '10');
            // get values to submit
            var form_data = form.serialize();
            // do ajax POST
            $.post(url, form_data, function(data) {
                nodeshot.overlay.hideLoading();
                // if valiadtion errors
                if ($(data).find('#success').length < 1) {
                    // unblock
                    $('#nodeshot-mask').css({
                        zIndex: 10,
                        opacity: 0.5
                    });
                    nodeshot.layout.$overlay.css('z-index', '11');
                    //form errors
                    nodeshot.layout.$overlay.html(data);
                    nodeshot.layout.$overlay = $('#nodeshot-overlay');
                    nodeshot.layout.$overlayInner = $('#nodeshot-overlay-inner');
                    // vertically center overlay
                    nodeshot.overlay.centerVertically();
                    // rebind events because we are not using $.live()
                    nodeshot.overlay.initClose();
                    nodeshot.overlay.bindCancelButton();
                    nodeshot.overlay.bindSubmitForm(function(form){
                        nodeshot.contact.submit(url, form);
                    });
                }
                // if succcess
                else {
                    // fade out mask
                    $('#nodeshot-overlay-inner').fadeOut(500, function(){
                        // send a message to the user
                        // TODO: needs translation
                        nodeshot.dialog.open(i18n.MESSAGE_SENT, nodeshot.overlay.close);
                    });
                }
                // reset sending
                nodeshot.sending = false;
            });
            // return false to prevent default form behaviour
            return false;
        }, // nodeshot.contact.submit()
        
        /*
        * nodeshot.contact.link()
        * binds click event that opens the overlay with the contact form
        */
        link: function(){
            $('#contact-link').click(function(e){
                // prevent link default behaviour
                e.preventDefault();
                nodeshot.contact.init(this.href);
                return false;
            });
        } // nodeshot.contact.link()
    },
    
    /*
     * nodeshot.node
     * add/edit node stuff
     */
    node: {
        
        /*
        * nodeshot.node.add()
        * opens a new overlay with the form to add a new node
        */
        add: function(){
            nodeshot.overlay.showMask();
            nodeshot.overlay.showLoading();
            // do ajax get to new node form
            $.get(nodeshot.url.index+'node/add/', function(data) {
                nodeshot.overlay.open(data);
                if (nodeshot.gmap.newMarker) {
                    // put lat and lng values of temporary gmap marker in the add node form
                    $("#id_lat").val(nodeshot.gmap.newMarker.getPosition().lat());
                    $("#id_lng").val(nodeshot.gmap.newMarker.getPosition().lng());
                    nodeshot.gmap.removeNewMarker();
                }
                // we are not using $.live() for performance reasons
                nodeshot.overlay.bindCancelButton();
                nodeshot.overlay.bindSubmitForm(function(form){
                    nodeshot.node.submit(form);
                });
            });
        }, // nodeshot.node.add()
        
        /*
        * nodeshot.node.submit(form:jQuery)
        * submits form to add a new node
        */
        submit: function(form){
            nodeshot.overlay.showLoading();
            // block form
            $('#nodeshot-mask').css({
                zIndex: 11,
                opacity: 0.7
            });
            nodeshot.layout.$overlay.css('z-index', '10');
            // get values to send
            var form_data = form.serialize();
            // do ajax POST
            $.post(nodeshot.url.index+'node/add/', form_data, function(data) {                
                nodeshot.overlay.hideLoading();
                // if validation errors
                if (data.length >= 10) {
                    // unblock form
                    $('#nodeshot-mask').css({
                        zIndex: 10,
                        opacity: 0.5
                    });
                    nodeshot.layout.$overlay.css('z-index', '11');
                    //form errors
                    nodeshot.layout.$overlay.html(data);
                    nodeshot.layout.$overlay = $('#nodeshot-overlay');
                    nodeshot.layout.$overlayInner = $('#nodeshot-overlay-inner');
                    // vertically center overlay
                    nodeshot.overlay.centerVertically();                    
                    // bind events again because we are not using $.live()
                    nodeshot.overlay.initClose();
                    nodeshot.overlay.bindCancelButton();
                    nodeshot.overlay.bindSubmitForm(function(form){
                        nodeshot.node.submit(form);
                    });
                }
                // if success
                else {
                    // fade out overlay
                    nodeshot.layout.$overlayInner.fadeOut(500, function(){
                        // send a nice message to the user
                        nodeshot.dialog.open(i18n.THANKYOU_NEWNODE_DIALOG, nodeshot.overlay.close);
                    });
                }
                nodeshot.layout.setFullScreen();
                nodeshot.sending = false;
            });
        }, // nodeshot.node.submit()
        
        /*
        * nodeshot.node.bindChangePassword()
        * binds event to the change password link in edit node form
        */
        bindChangePassword: function(){
            // bind click event
            $('#change-password').click(function(e){
                // cache $(this) in a local var
                var $this = $(this);
                // cache password field
                var password_field = $('#id_new_password');
                // if password fields are hidden we need to show them
                if($this.data('info')==undefined || $this.data('info').status==0){
                    // set jquery data
                    $this.data('info', {
                        // current password
                        text: $this.text(),
                        // status (1: shown, 0: hidden)
                        status: 1
                    });
                    // change text of link
                    $this.text(i18n.CANCEL);
                    // clear new password value if necessary
                    $('#id_new_password2').val('');
                    // hide fake password field
                    $('#id_fake_password').hide();
                    // show real password fields
                    password_field.val('').show(500);
                    $('#verify-password').show(500);   
                }
                // if password field are shown we need to hide them
                else{
                    // change text of link to its original value previously stored with jquery.data
                    $this.text($this.data('info').text);
                    // clear passowrd value
                    $('#id_new_password2').val('');
                    // show back fake password field
                    $('#id_fake_password').show(500);
                    // hide real password fields
                    password_field.val('').hide();
                    $('#verify-password').hide();
                    // set status as 0, meaning password fields are hidden
                    $this.data('info').status = 0;
                }
            });
            
            if($('#non-field-errors').length > 0){
                $('#change-password').click();
            }
        } // nodeshot.node.bindChangePassword()
        
    }, // nodeshot.node
    
    /*
     * nodeshot.advanced
     * advanced information about devices and interfaces in a node
     */
    advanced: {
        
        /*
        * nodeshot.advanced.init()
        * init jquery ui tabs and +info buttons in advanced node info
        */
        init: function(){
            // if is the first time we're loading the tab
            nodeshot.advanced.firstTimeLoadingTab = true;
            // init jquery tabs
            $('#advanced-info').tabs({
                fx: { opacity: 'toggle', height: 'toggle', duration: 400 },
                // when tab is shown
                show: function(e, ui){
                    // if first time is loaded
                    if(nodeshot.advanced.firstTimeLoadingTab){
                        // center overlay vertically without animation
                        nodeshot.overlay.centerVertically();
                        // not first time anymore
                        nodeshot.advanced.firstTimeLoadingTab = false;
                    }
                    // else we are changing tab
                    else{
                        // center overlay vertically with animation
                        nodeshot.overlay.centerVertically(true, 400);
                    }
                }
            });
            // toggle +info or -info
            var $info = $('.toggle-info', '#advanced-info').toggle(
                // show
                function(){
                    // cache $(this) object
                    var $this = $(this);
                    // find tbody.additional and show it with a nice animation
                    $this.parent().parent().parent().parent().find('.additional').show(300, function(){
                        // re-center overlay vertically
                        nodeshot.overlay.centerVertically(true, 300);
                    });
                    // +info green button becomes -info red button
                    $this.removeClass('green');
                    $this.addClass('red');
                    $this.text(i18n.LESSINFO);
                },
                // hide
                function(){
                    // cache $(this)
                    var $this = $(this);
                    // find tbody.additional and hide it with a nice animation
                    $this.parent().parent().parent().parent().find('.additional').hide(300, function(){
                        // re-center overlay vertically
                        nodeshot.overlay.centerVertically(true, 300)
                    });
                    // -info red button becomes +info green button
                    $this.removeClass('red');
                    $this.addClass('green');
                    $this.text(i18n.MOREINFO);
                }
            )
            // if no additional info don't show the + info button
            var length = $info.length;
            for(var i=0; i<length; i++){
                if($info.eq(i).parent().parent().parent().parent().find('.additional tr').length < 1){
                    $info.eq(i).hide();
                }
            }
        } // nodeshot.advanced.init()
        
    }, // nodeshot.advanced

    /*
     * nodeshot.azimuth
     * azimuth calculation stuff
     */
    azimuth: {
        // Calculate azimuth between two points
        calculate: function(from_lat, from_lng, to_lat, to_lng) {
            //var dLat = (to_lat-from_lat).toRad();
            //var dLon = (to_lng-from_lng).toRad();
            //var lat1 = from_lat.toRad();
            //var lat2 = to_lat.toRad();
            //var y = Math.sin(dLon) * Math.cos(lat2);
            //var x = Math.cos(lat1)*Math.sin(lat2) - Math.sin(lat1)*Math.cos(lat2)*Math.cos(dLon);
            //var brng = Math.atan2(y, x).toDeg();
            // round distance 4 decimals
            //brng = Math.round(brng*Math.pow(10,5))/Math.pow(10,5);
            //return brng;
            var fromLatlng = new google.maps.LatLng(from_lat, from_lng);
            var toLatlng = new google.maps.LatLng(to_lat, to_lng);
            return google.maps.geometry.spherical.computeHeading(fromLatlng, toLatlng);
        }
    },
    /*
     * nodeshot.distance
     * distance calculation stuff
     */
    distance: {
        
        // here we'll store the new calculated distances
        links: [],
        
        /*
        * nodeshot.distance.calculate(from_lat:float, from_lng:float, to_lat:float, to_lng:float, unit:string)
        * distance calculation stuff
        */
        calculate: function(from_lat, from_lng, to_lat, to_lng, unit) {
            var radlat1 = Math.PI * from_lat/180;
            var radlat2 = Math.PI * to_lat/180;
            var theta = from_lng-to_lng;
            var radtheta = Math.PI * theta/180;
            var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
            dist = Math.acos(dist);
            dist = dist * 180/Math.PI;
            dist = dist * 60 * 1.1515;
            if (unit=="K") { dist = dist * 1.609344 };
            // I would like to know if this is to calculate the miles?
            if (unit=="N") { dist = dist * 0.8684 };
            // round distance 2 decimals
            dist = Math.round(dist*Math.pow(10,2))/Math.pow(10,2);
            return dist;
        }, // nodeshot.distance.calculate()
        
        /*
        * nodeshot.distance.add(link:object, data:object, distance:string, saved:boolean)
        * add a new calculated distance link
        */
        add: function(link, data, distance, saved){
            // push object into nodeshot.distance.links and store the index
            var index = this.links.push({
                // google.maps.Polyline object
                link: link,
                // start node name
                from_name: data.from_name,
                // destination node name
                to_name: data.to_name,
                // prepare $div property that will contain jquery object with link info
                $div: null,
                // remove link method
                remove: function(){
                    // if there is any saved link
                    if(nodeshot.distance.saved_links){
                        var found = false;
                        // upcount negative while loop
                        var len = nodeshot.distance.saved_links.length + 1;
                        var ilen = len - 1;
                        while(--len){
                            // link in local variable
                            var link = nodeshot.distance.saved_links[ilen-len];
                            // if we find the link
                            if(link && link.from_name == this.from_name && link.to_name == this.to_name){
                                // remove it
                                nodeshot.distance.saved_links.remove(ilen-len);
                                // set local var found to true
                                found = true;
                            }
                        }
                        // if link we are removing has been found in the saved links
                        if(found){
                            // we need to update the cookie containing the saved links
                            $.cookie('nodeshot_saved_distances', JSON.stringify(nodeshot.distance.saved_links), { expires: 365, path: nodeshot.url.index });
                        }
                    }
                    // hide link from gmap
                    this.link.setMap(null);
                    // remove HTML link info
                    this.$div.fadeOut(500, this.$div.remove);
                    // delete link object
                    delete this.link;
                },
                // hide link method
                hide: function(){
                    // hide link from gmap
                    this.link.setMap(null);
                    // hide a.link-hide
                    this.$div.find('.link-hide').hide();
                    // show a.link-show
                    this.$div.find('.link-show').show();
                },
                // show link method
                show: function(){
                    // show link on gmap
                    this.link.setMap(nodeshot.gmap.map);
                    // i bet you know
                    this.$div.find('.link-show').hide();
                    this.$div.find('.link-hide').show();                    
                },
                // save link method
                save: function(){
                    // saved is from add: function(link, data, distance, saved)
                    // and sincerely i don't remember anymore why this is here but we surely need it for some reason or another
                    if(saved){
                        return false;
                    }
                    // hide save button
                    this.$div.find('.link-save').fadeOut(500);
                    // if no cookie set
                    if(nodeshot.distance.cookie == null){
                        // convert current object to json string
                        var json_string = JSON.stringify([data]);
                    }
                    // if there is a cookie with saved stuff
                    else{
                        // add this distance link to the array
                        nodeshot.distance.saved_links.push(data);
                        // convert back to JSON string
                        var json_string = JSON.stringify(nodeshot.distance.saved_links);
                    }
                    // save the cookie with the JSON string
                    $.cookie('nodeshot_saved_distances', json_string, { expires: 365, path: nodeshot.url.index });
                }
            });
            // another thing I forgot to comment and now i don't remember why I did it
            index = index - 1;
            // prepare href of links to nodes
            var fromNode = 'nodeshot.nodes.'+nodeshot.status_choices[data.from_status]+'.'+data.from_slug
            var toNode = 'nodeshot.nodes.'+nodeshot.status_choices[data.to_status]+'.'+data.to_slug
            // prepare html of links
            var from_link = '<a class="link-node" href="javascript:nodeshot.gmap.goToNode(\''+fromNode+'\')">'+data.from_name+'</a>';
            var to_link = '<a class="link-node" href="javascript:nodeshot.gmap.goToNode(\''+toNode+'\')">'+data.to_name+'</a>';
            // prepare html to insert
            var html = '<div id="distance-link'+index+'" class="distance-link"><span>'+from_link+' - '+to_link+': <b>'+distance+' km</b> ';
            html = html +   '<a href="javascript:nodeshot.distance.links['+index+'].show()" class="link-show">'+i18n.SHOW+'</a>';
            html = html +   '<a href="javascript:nodeshot.distance.links['+index+'].hide()" class="link-hide">'+i18n.HIDE+'</a>';
            if(!saved){
                html = html +   '<a href="javascript:nodeshot.distance.links['+index+'].save()" class="link-save">'+i18n.SAVE+'</a>';
            }
            html = html +   '<a href="javascript:nodeshot.distance.links['+index+'].remove()" class="link-remove">'+i18n.DELETE+'</a>';
            html =html+'</span></div>';
            // inject HTML link info (hidden)
            nodeshot.layout.$sideLinks.prepend(html);
            // cache jquery object
            this.links[index].$div =  $('#distance-link'+index);
            // show HTML link info
            this.links[index].$div.fadeIn(500);
            // layout might need this ;-)
            nodeshot.layout.setFullScreen();
        } // nodeshot.distance.add()
        
    }, // nodeshot.distance
    
    /*
    * nodeshot.distance.add(link:object, data:object, distance:string, saved:boolean)
    * add a new calculated distance link
    */
    gmap: {
        
        // here we'll store new nodes marker and listener
        newMarker: '',
        newMarkerListener: '',
        clickListener: '',
        // here we'll store infoWindow object
        infoWindow: new google.maps.InfoWindow,
        
        /*
        * nodeshot.gmap.init()
        * initializes google map
        */
        init: function(){
            // cache jquery objects
            nodeshot.layout.$map = $('#map_canvas');
            nodeshot.layout.$sideLinks = $('#side-links');
            // init latlng object with coordinates specified in settings.py
            var latlng = new google.maps.LatLng(nodeshot.gmap.map_center.lat, nodeshot.gmap.map_center.lng);
            // init gmpap 
            nodeshot.gmap.map = new google.maps.Map(document.getElementById('map_canvas'), {
                zoom: 12,
                center: latlng,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            });
            // init geocoder
            nodeshot.gmap.geocoder = new google.maps.Geocoder();
            // if nodeshot.nodes hasn't been populaetd yet wait 250 ms and retry until it has been populated
            var intervalId = setInterval(function(){
                // if not populated wait and retry
                if(nodeshot.nodes.active!=undefined){
                    // when we finally get it stop repeating the function
                    clearInterval(intervalId);                    
                    // draw nodes
                    nodeshot.gmap.drawNodes(nodeshot.status_choices.a);
                    nodeshot.gmap.drawNodes(nodeshot.status_choices.h);
                    // if $potential checkbox is checked
                    if(nodeshot.layout.$potential[0].checked){
                        nodeshot.gmap.drawNodes(nodeshot.status_choices.p);
                    }                    
                    // if map center is not the default one
                    if(!nodeshot.gmap.map_center.is_default){                        
                        /*
                        split value in two variables, one for slug and one for status
                        example:
                            'sephiroth;a'
                        becomes:
                            slug = 'sephiroth'
                            status = nodeshot.status_choices['a']
                            which becomes
                                status = 'active'
                            therefore
                                nodeshot.nodes[status][slug]
                            becomes
                                nodeshot.nodes['active']['sephiroth']
                            which is the same as
                                nodeshot.nodes.active.sephiroth
                        */
                        var bits = nodeshot.gmap.map_center.node.split(';');
                        var slug = bits[0];
                        var status = nodeshot.status_choices[bits[1]];
                        // center map and open the node
                        nodeshot.gmap.goToNode(nodeshot.nodes[status][slug]);
                    }
                }
            }, 200);
            nodeshot.layout.setFullScreen();
        }, // nodeshot.gmap.init()
        
        /*
        * nodeshot.gmap.drawNodes(status:string)
        * draw nodes of the specified status
        */
        drawNodes: function(status) {
            // shortcut to the object we need
            var data = nodeshot.nodes[status];
            // marker icon depends on the status (green = active, blue = hotspot, orange = potential)
            var image = nodeshot.url.media+'images/marker_'+status+'.png';
            
            for(var node in data) {
                // save marker in current node object
                var latlng = new google.maps.LatLng(data[node].lat, data[node].lng);
                data[node].marker = new google.maps.Marker({
                    position: latlng,
                    map: nodeshot.gmap.map,
                    title: data[node].name,
                    icon: image
                });
                data[node].marker.slug = data[node].slug;
                // show marker on gmap
                data[node].marker.setMap(nodeshot.gmap.map);
                // add event listener
                data[node].listener = google.maps.event.addListener(data[node].marker, 'click',  nodeshot.gmap.clickMarker(data[node].marker, data[node]));
            }
            // draw links if status is active
            if (status == nodeshot.status_choices.a) {
                // cache length for upcount negative while loop
                var len = nodeshot.nodes.links.length + 1;
                var ilen = len - 1;
                // determine which link quality calculation method we should use
                var quality = nodeshot.layout.$linkQuality.find('input:checked').val();
                // this is performant on modern browsers
                while(--len){
                    // shortcut to link
                    var link = nodeshot.nodes.links[ilen-len];
                    // draw link from ... to ...
                    /*
                    writing
                        quality = 'dbm';
                        link[quality]
                    is the same as writing
                        link.dbm
                    */
                    link.gmap = nodeshot.gmap.drawLink(link.from_lat, link.from_lng, link.to_lat, link.to_lng, link[quality]);
                }
            }
        }, // nodeshot.gmap.drawNodes()
        
        /*
        * nodeshot.gmap.removeMarkers(status:string)
        * removes nodes of the specified status
        */
        removeMarkers: function(status) {
            // loop over nodes with the specified status and remove them from gmap
            for(var node in nodeshot.nodes[status]){
                // remove from gmap
                nodeshot.nodes[status][node].marker.setMap(null);
                // remove listener
                google.maps.event.removeListener(nodeshot.nodes[status][node].listener);
                delete nodeshot.nodes[status][node].marker;
                delete nodeshot.nodes[status][node].listener;
                //// remove from gmap
                //if(nodeshot.nodes[status][node].marker){
                //    nodeshot.nodes[status][node].marker.setMap(null);
                //    // remove listener
                //    google.maps.event.removeListener(nodeshot.nodes[status][node].listener);
                //}
            }
            // remove links if removing active nodes
            if(status==nodeshot.status_choices.a){
                this.removeLinks();
            }
        }, // nodeshot.gmap.removeMarkers()
        
        /*
        * nodeshot.gmap.removeLinks()
        * removes links
        */
        removeLinks: function(){
            var len = nodeshot.nodes.links.length + 1;
            var ilen = len - 1;
            while(--len){
                nodeshot.nodes.links[ilen-len].gmap.setMap(null);
                delete nodeshot.nodes.links[ilen-len].gmap;
            }
        }, // nodeshot.gmap.removeLinks()
        
        /*
        * nodeshot.gmap.goToNode(node:object|string)
        * center map to specified node, zoom a little bit and trigger click on the marker
        */
        goToNode: function(node) {
            // if destination is a potential node and $potential is unchecked show potential nodes
            nodeshot.gmap.check$potential(nodeshot.status_choices[node.status]);
            // if node is a string it means we have to evaluate the string to get the object
            if(typeof(node)=='string'){
                node = eval(node);
            }
            // check if there is a google.maps.Marker object
            if (node.marker) {
                // trigger click event
                google.maps.event.trigger(node.marker, 'click');
                // center gmap
                nodeshot.gmap.map.panTo(node.marker.getPosition());
                // zoom a little bit
                nodeshot.gmap.map.setZoom(13);
            } else {
                // node not found
                nodeshot.dialog.open('Il nodo non esiste.');
            }
        }, // nodeshot.gmap.goToNode()
        
        /*
        * nodeshot.gmap.newNodeMarker(location:obj)
        * add new node marker
        */
        newNodeMarker: function(location) {
            // remove any new marker previously inserted
            nodeshot.gmap.removeNewMarker();
            // new google.maps.Marker object
            var marker = new google.maps.Marker({
                position: location,
                map: nodeshot.gmap.map,
                icon: nodeshot.url.media+'images/marker_new.png'
            });
            // prepare HTML for infoWindow
            var contentString = '<div id="confirm-new"><h2>'+i18n.NEWNODE_INFOWINDOW_TITLE+'</h2>'+
                '<a href="javascript:nodeshot.node.add()" class="green">'+i18n.YES+'</a>'+
                '<a href="javascript:nodeshot.gmap.removeNewMarker()" class="red">'+i18n.NO+'</a></div>'
            // set content of infoWindow
            nodeshot.gmap.infoWindow = new google.maps.InfoWindow({
                content: contentString
            });
            // open infoWindow
            nodeshot.gmap.infoWindow.open(nodeshot.gmap.map,marker);
            // add listener
            nodeshot.gmap.newMarkerListener = google.maps.event.addListener(marker, 'click', function() {
                nodeshot.gmap.infoWindow.open(nodeshot.gmap.map,marker);
            });
            nodeshot.gmap.newMarker = marker;
        }, // nodeshot.gmap.newNodeMarker()
        
        /*
        * nodeshot.gmap.removeNewMarker()
        * remove new marker when adding a new node
        */
        removeNewMarker: function(){
            // hide from gmap
            if (nodeshot.gmap.newMarker){ 
                nodeshot.gmap.newMarker.setMap(null);
            }
            // remove listener
            if (nodeshot.gmap.newMarkerListener){
                google.maps.event.removeListener(nodeshot.gmap.newMarkerListener);
            }
            // reset
            nodeshot.gmap.newMarker = null;
            nodeshot.gmap.newMarkerListener = null;
        }, // nodeshot.gmap.removeNewMarker()
        
        /*
        * nodeshot.gmap.clickMarker(marker:object, node:object)
        * triggers click on marker
        */
        clickMarker: function(marker, node) {
            return function() {
                // if overlay is open
                if(nodeshot.layout.$overlay){
                    // close it first
                    nodeshot.overlay.close();
                }
                nodeshot.overlay.showMask(0.7);
                nodeshot.overlay.showLoading();
                $.get(nodeshot.url.index+'node/info/'+node.id+'/', function(data) {
                    // remove listener in case it has already been set
                    if(nodeshot.gmap.infoWindow.domready){
                        google.maps.event.removeListener(nodeshot.gmap.infoWindow.domready);
                    }
                    // add listener to domready of infowindows - it will be triggered when the infoWindow is ready
                    nodeshot.gmap.infoWindow.domready = google.maps.event.addListener(nodeshot.gmap.infoWindow, 'domready', function(){
                        $(".tabs").tabs({
                            // save height of first tab for comparison
                            create: function(e, ui){
                                // cache $(this)
                                $this = $(this);
                                // save height of active tab in nodeshot object
                                nodeshot.tab0Height = $this.find('.ui-tabs-panel').eq($this.tabs('option', 'selected')).height();
                            },
                            // change height of tab if tab is shorter
                            show: function(e, ui){
                                // cache object
                                $this = $(this);
                                // if distance tab
                                if($this.tabs('option', 'selected')===1){
                                    // cache object
                                    var tab = $this.find('.ui-tabs-panel').eq(1);
                                    // save this height
                                    nodeshot.tab1Height = tab.height();
                                    // compare and if first tab was higher set the same height
                                    if(nodeshot.tab0Height > nodeshot.tab1Height){
                                        tab.height(nodeshot.tab0Height);
                                    }
                                }
                            },
                            // advanced tab
                            select: function(e, ui){
                                if(ui.tab.id=='advanced-link'){
                                    nodeshot.overlay.showMask(0.8, true);
                                    nodeshot.overlay.showLoading();
                                    $.get($(ui.tab).attr('data-url'), function(data) {
                                        // open overlay, closeOnClick = true
                                        nodeshot.overlay.open(data, true);
                                        // init controls
                                        nodeshot.advanced.init();
                                        // we are not using $.live() for performance reasons
                                        nodeshot.overlay.bindCancelButton();
                                    });
                                    return false
                                }                                
                            }
                        });
                        nodeshot.contact.link();
                        var search_input = $('#distance-search');
                        nodeshot.layout.bindFocusBlur(search_input);
                        // Implements the search function
                        search_input.autocomplete({
                            minLength: 3,
                            // where to take values from
                            source: function(request, response) {
                                // store term in a local var
                                var term = request.term;
                                // check if term has already requested before
                                if (term in nodeshot.searchCache) {
                                    // if has been found return the term in the cache
                                    response(nodeshot.searchCache[term]);
                                    return;
                                }
                                // if term has not been found in the cache go ahead with a new request
                                lastXhr = $.getJSON(nodeshot.url.index+'search/'+request.term+'/', function(data, status, xhr) {
                                    // cache the term
                                    if (xhr === lastXhr && data != null && data.length > 0){
                                        nodeshot.searchCache[term] = data;
                                        response(data);
                                    }
                                    else{
                                        nodeshot.searchCache[term] = '';
                                        response('');
                                    }
                                });
                            },
                            // when en item in the menu is clicked
                            select: function(e, ui) {
                                nodeshot.gmap.drawDistanceLink({
                                    from_name: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].name,
                                    from_slug: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].jslug,
                                    from_lat: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].lat,
                                    from_lng: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].lng,
                                    from_status: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].status,
                                    to_name: ui.item.name,
                                    to_slug: ui.item.value,
                                    to_lat: ui.item.lat,
                                    to_lng: ui.item.lng,
                                    to_status: ui.item.status
                                });
                                search_input.val(ui.item.label)
                                return false;
                            },
                            // when a menu in the item is selected / focused
                            focus: function(e, ui){
                                // put label on input
                                $(this).val(ui.item.label);
                                // return false to avoid default autocomplete plugin behaviour
                                return false;
                            }
                        });
                        // we don't need to cache #distance-select cos this is the only time we access it
                        $('#distance-select').change(function(){
                            // cache $(this)
                            var $this = $(this);
                            // split values in array
                            var values = ($this.val()).split(';');
                            // replace comma
                            var to_lat = (values[0]).replace(",",".");
                            var to_lng = (values[1]).replace(",",".");
                            var to_slug = values[2];
                            var to_status = values[3]
                            // calculate distance and add controls
                            nodeshot.gmap.drawDistanceLink({
                                from_name: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].name,
                                from_slug: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].jslug,
                                from_lat: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].lat,
                                from_lng: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].lng,
                                from_status: nodeshot.nodes[nodeshot.status_choices[node.status]][node.jslug].status,
                                to_name: $this.find('option[value="'+$this.val()+'"]').text(),
                                to_slug: to_slug,
                                to_lat: to_lat,
                                to_lng: to_lng,
                                to_status: to_status
                            });
                        });
                        // readjust dimensions
                        nodeshot.layout.setFullScreen();
                        // this is a fix needed for certain cases
                        setTimeout(function(){nodeshot.layout.setFullScreen()}, 300);
                    });
                    nodeshot.gmap.infoWindow.setContent(data);
                    nodeshot.gmap.infoWindow.maxWidth = 500;
                    nodeshot.gmap.infoWindow.open(nodeshot.gmap.map, marker);
                    nodeshot.overlay.hideLoading();
                    // remove mask only if there isn't any dialog
                    if(!nodeshot.layout.$dialog){
                        nodeshot.overlay.hideMask();
                    }
                });
            };
        }, // nodeshot.gmap.clickMarker()
        
        /*
        * nodeshot.gmap.drawLink(from_lat:float, from_lng:float, to_lat:float, to_lng:float, quality:int)
        * draws a link on google map
        */
        drawLink: function(from_lat, from_lng, to_lat, to_lng, quality) {
            // determine color depending on link quality
            // instead of using a switch or a concatenation of if/else, we'll use an array to save space ;-)
            var color = [
                null, // skip 0
                '#00ff00', // quality == 1: Good
                '#fcfd00', // quality == 2: Medium
                '#ee0000', // quality == 3: Bad
                '#5f0060'  // quality == 4: used for distance calculations
            ];
            var opacity = 0.5;
            // if link color is yellow increase opacity
            if(quality==2){
                opacity = 0.9;
            }
            // draw link on gmap
            var link = new google.maps.Polyline({
                // coordinates
                path: [new google.maps.LatLng(from_lat, from_lng),new google.maps.LatLng(to_lat, to_lng)],
                // line features
                strokeColor: color[quality], // quality can be 1,2,3 or 4
                strokeOpacity: opacity,
                strokeWeight: 5 
            });
            // show link on gmap
            link.setMap(nodeshot.gmap.map);
            // return link object - needed by nodeshot.distance.add()
            return link;
        }, // nodeshot.gmap.drawLink()
        
        /*
        * nodeshot.gmap.drawLink(data:object, saved:boolean)
        * draws a distance link on google map
        */
        drawDistanceLink: function(data, saved){
            // if data is not right stop here
            if(!data){
                return false;
            }
            if(data.from_slug==data.to_slug){
                nodeshot.dialog.open(i18n.DESTINATION_NOTVALID);
                return false;
            }
            // ensure coords are float type
            data.from_lat = parseFloat(data.from_lat);
            data.from_lng = parseFloat(data.from_lng);
            data.to_lat = parseFloat(data.to_lat);
            data.to_lng = parseFloat(data.to_lng);
            // if destination is a potential node and $potential is unchecked show potential nodes
            nodeshot.gmap.check$potential(nodeshot.status_choices[data.to_status])
            // check potentail checkbox if needed
            this.check$potential(nodeshot.status_choices[data.from_status]);            
            this.check$potential(nodeshot.status_choices[data.to_status]);
            // draw link on map and save it in a local variable
            var link = nodeshot.gmap.drawLink(data.from_lat, data.from_lng, data.to_lat, data.to_lng, 4);
            // calculate distance
            var distance = nodeshot.distance.calculate(data.from_lat, data.from_lng, data.to_lat, data.to_lng, "K");
            // calculate azimuth
            var azimuth = nodeshot.azimuth.calculate(data.from_lat, data.from_lng, data.to_lat, data.to_lng);
            // innerHTML
            $('#result').html(distance);
            $('#azimuth').html(azimuth);
            // show result
            $('#result-row').fadeIn(500);
            // add distance link controls
            nodeshot.distance.add(link, data, distance, saved);
            return true;
        }, // nodeshot.gmap.drawDistanceLink()
        
        /*
        * nodeshot.gmap.removeAddressMarker()
        * removes marker after an address has been searched
        */
        removeAddressMarker: function(){
            nodeshot.gmap.addressMarker.setMap(null);
            delete nodeshot.gmap.addressMarker;
        }, // nodeshot.gmap.removeAddressMarker()
        
        /*
        * nodeshot.gmap.check$potential(status:string)
        * shows potential if needed
        */
        check$potential: function(status){
            // if is a potential node and potential checkbox is unchecked
            if (status == nodeshot.status_choices.p && !nodeshot.layout.$potential[0].checked) {
                // check the checkbox
                nodeshot.layout.$potential[0].checked = true
                // show nodes
                nodeshot.gmap.drawNodes(nodeshot.status_choices.p);
                // remember
                $.cookie('nodeshot_potential_nodes', 'true', { expires: 365, path: nodeshot.url.index });
            }
        }, // nodeshot.gmap.check$potential()
        
        /*
        * nodeshot.gmap.searchAddress(address:string, input:jQuery)
        * sarchs for an address on google map
        */
        searchAddress: function(address, input){
            if (nodeshot.gmap.geocoder) {
                // gmap geocode
                nodeshot.gmap.geocoder.geocode({ 'address': address }, function (results, status) {
                    // if address has been found
                    if (status == google.maps.GeocoderStatus.OK) {
                        // remove mask
                        nodeshot.overlay.hideMask();
                        // save actions in this function that will be executed later
                        var moveMap = function(results){
                            var latlng = new google.maps.LatLng(results[0].geometry.location.lat(), results[0].geometry.location.lng());
                            if(nodeshot.gmap.addressMarker){
                                nodeshot.gmap.removeAddressMarker();
                            }
                            nodeshot.gmap.addressMarker = new google.maps.Marker({
                                position: latlng,
                                map: nodeshot.gmap.map
                            });
                            nodeshot.gmap.map.panTo(latlng);
                            nodeshot.gmap.map.setZoom(16);
                        }
                        // if overlay hasn't been moved yet
                        if(!nodeshot.layout.$overlayInner.hasClass('ui-draggable')){
                            nodeshot.layout.$overlayInner.css({
                                top: nodeshot.layout.$overlayInner.css('margin-top'),
                                left: (nodeshot.layout.$overlayInner.position()).left,
                                position: 'absolute',
                                marginTop: 0
                            })
                            nodeshot.layout.$overlay.css({
                                width: 0,
                                height: 0
                            });
                            nodeshot.layout.$overlayInner.animate({
                                top: 50,
                                left: 80
                            },
                            // when animation is finished
                            function(){
                                // make the overlay draggable
                                nodeshot.layout.$overlayInner.draggable();
                                // update google map
                                moveMap(results);
                            });
                        }
                        // if overlay has already been moved
                        else{
                            // just update google map
                            moveMap(results);
                        }
                    }
                    // if address not found
                    else {
                        input.addClass('error');
                    }
                });
            }
        }, // nodeshot.gmap.searchAddress()
        
        /*
        * nodeshot.gmap.unload()
        * unloads google map
        */
        unload: function(){
            delete nodeshot.layout.$map;
            delete nodeshot.layout.$sideLinks;
            this.removeMarkers(nodeshot.status_choices.a);
            this.removeMarkers(nodeshot.status_choices.h);
            // if $potential checkbox is checked - we need this otherwise we'll get an error
            if(nodeshot.layout.$potential[0].checked){
                this.removeMarkers(nodeshot.status_choices.p);
            }      
            delete nodeshot.gmap.map;
            delete nodeshot.gmap.geocoder;
        }
        
    }, // nodeshot.gmap
    
    /*
    * nodeshot.infoTab
    * infoTab stuff
    */
    infoTab:{
        
        /*
        * nodeshot.infoTab.init()
        * initialize info tab
        */
        init: function(){
            // cache jquery objects
            nodeshot.layout.$infoTable = $("#info-table")
            nodeshot.layout.$infoWrapper = $('#info-wrapper');
            nodeshot.layout.$tableWrapper = $('#table-wrapper');
            nodeshot.layout.$signalbar = $(".signalbar");
            nodeshot.layout.$body.append('<script src="'+nodeshot.url.media+'js/compressed/overview.js"></script>')
        }, // nodeshot.infoTab.init()
        
        /*
        * nodeshot.infoTab.init2()
        * inits tablesorter and progressbar
        * it's called after an additional javascript file has been downloaded
        */
        init2: function(){
            nodeshot.layout.$infoTable.tablesorter();
            // up count negative while loop is more performant on modern browsers
            len = nodeshot.layout.$signalbar.length + 1;
            ilen = len - 1;
            while(--len){
                var obj = nodeshot.layout.$signalbar.eq(ilen-len);
                var value = obj.attr('data-value');
                // init progress bar
                var defaults = {
                    showText: false,
                    boxImage: nodeshot.url.media+'/images/progressbar.gif',
                    barImage: {
                        0:	nodeshot.url.media+'/images/progressbg_red.gif',
                        30: nodeshot.url.media+'/images/progressbg_orange.gif',
                        45: nodeshot.url.media+'/images/progressbg_yellow.gif',
                        70: nodeshot.url.media+'/images/progressbg_green.gif'
                    }
                }
                obj.progressBar(value, defaults);
            }
        }, // nodeshot.infoTab.init2()
        
        /*
        * nodeshot.infoTab.scrollTo(name:string)
        * scroll to the specified object with a nice animation
        */
        scrollTo: function(name){
            // cache object
            var to = $('tr.'+name);            
            // if target is found
            if(to.length>0){
                // define how much scrolling is needed
                var scroll = nodeshot.layout.$tableWrapper.scrollTop() + to.position().top - 100
                // scrolling animation
                nodeshot.layout.$tableWrapper.animate({scrollTop: scroll},'slow', function(){
                    // when animation is finished find the row
                    var row = to.find('td');
                    // change its background color to highlight it
                    row.css('background-color', '#ffffc8');
                    // then change it back to white background
                    setTimeout(function(){
                        row.css('background-color', '#fff');
                    }, 3000)
                });
            }
            // if target not found return a message
            else{
                setTimeout(function(){
                    // TODO: translate
                    nodeshot.dialog.open('Il nodo selezionato non è presente in questa lista.')
                }, 300);
            }
        }, // nodeshot.infoTab.scrollTo()
        
        /*
        * nodeshot.infoTab.unload()
        * unloads infoTab
        */
        unload: function(){
            delete nodeshot.layout.$infoTable;
            delete nodeshot.layout.$infoWrapper;
            delete nodeshot.layout.$tableWrapper;
            delete nodeshot.layout.$signalbar;
        } // nodeshot.infoTab.unload()
        
    }, // ndoeshot.infoTab
    
    /*
    * nodeshot.easterEgg()
    * initialize easter egg, idea by OrazioPirataDelloSpazio
    */
    easterEgg: function(){
        // press these keys in order and you'll see some magic ;-)
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
    } // nodeshot.easterEgg()

} // nodeshot
