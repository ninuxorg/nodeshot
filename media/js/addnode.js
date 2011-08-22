/*  This file contains all the functions to add/modify information about a new/existing node
 */

var nodeshot = {
    
    init: function(){
        nodeshot.layout.cacheObjects();
        nodeshot.layout.initSideControl();
        nodeshot.layout.initSearchAddress();
        nodeshot.distance.remember();
    },
    
    /*
     * nodeshot.layout
     * handle the css dynamically
     */
    layout:{
        /*
        * nodeshot.layout.cacheObjects()
        * caches some jquery objects
        */
        cacheObjects: function(){
            this.$body = $('body');
            this.$container = $('#container');
            this.$header = $('#header');
            this.$content = $('#content');
            this.$aside = $('#aside');
            this.$map = $('#map_canvas');
            this.$sideLinks = $('#side-links');
            this.$nodeTreeContainer = $('#node-tree-container');
            this.$hideSide = $('#hide-side');
        },
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
            else{
                this.$infoWrapper.height($window.height()-this.$header.height());
            }
            // set nodeTreeContainer height if not too short
            var newTreeHeight = this.$container.height()-this.$header.height()-(this.$nodeTreeContainer.position()).top;
            if(newTreeHeight > 200){
                this.$nodeTreeContainer.height(newTreeHeight);
            }
        },
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
                //position:'absolute',
                marginTop: this.$header.height()
                //right: 0
            });
        },
        /*
        * nodeshot.layout.getCssInt()
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
        },
        /*
        * nodeshot.layout.horizontalCenter()
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
        },
        /*
        * nodeshot.layout.verticalCenter()
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
        },
        /*
        * nodeshot.layout.bindFocusBlue(obj)
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
        },
        /*
        * nodeshot.layout.initSearchAddress()
        * search an address on google maps
        */
        initSearchAddress: function(){
            $('#search-address').click(function(e){
                e.preventDefault();
                if(infoWindow){
                    infoWindow.close()
                }
                nodeshot.overlay.addMask();
                var data = '<div id="nodeshot-overlay-inner" class="content narrower"><div id="gmap-search"><h3>Cerca un\'indirizzo</h3><p>Inserisci l\'indirizzo completo</p><p><input type="text" class="text" id="gmap-address" /><input class="button" type="submit" value="Cerca" id="gmap-submit" /></p></div></div>';
                nodeshot.overlay.open(data, false, removeNewMarker);
                
                var input = $('#gmap-address');
                
                // bind keyup of search field
                input.bind('keyup', function(e) {
                    var code = (e.keyCode ? e.keyCode : e.which);
                    // if pressing enter
                    if (code == 13 && input.val()!=''){
                        nodeshot.layout.searchAddress(input.val(), input);
                    }
                    // if just typing
                    else{
                        // remove eventual error class
                        if(input.hasClass('error')){
                            input.removeClass('error');
                        }
                    }
                });
                $('#gmap-submit').click(function(){
                    nodeshot.layout.searchAddress(input.val(), input);
                });
            });
        },
        searchAddress: function(address, input){
            if (geocoder) {
                // gmap geocode
                geocoder.geocode({ 'address': address }, function (results, status) {
                    // if address has been found
                    if (status == google.maps.GeocoderStatus.OK) {
                        // remove mask
                        nodeshot.overlay.removeMask();
                        // save actions in this function that will be executed later
                        var moveMap = function(results){
                            var latlng = new google.maps.LatLng(results[0].geometry.location.lat(), results[0].geometry.location.lng());
                            if(nodeshot.gmap.addressMarker){
                                nodeshot.gmap.removeAddressMarker();
                            }
                            nodeshot.gmap.addressMarker = new google.maps.Marker({
                                position: latlng,
                                map: map
                            });
                            map.panTo(latlng);
                            map.setZoom(16);
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
        },
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
                });
                // enlarge the content with an animation
                nodeshot.layout.$content.animate({width: nodeshot.layout.$header.width()},500,function(){
                    nodeshot.layout.$showColumn.show(500);
                });
                // reset dimensions and re-enable scrollbar with some delay
                setTimeout(function(){
                    nodeshot.layout.setFullScreen();
                    // re-enable scrollbar
                    nodeshot.layout.$body.css('overflow', 'auto');
                }, 600);
                // save cookie to remember this choice
                $.cookie('nodeshot_sidebar', 'false', { expires: 365, path: __project_home__ });
            });
            this.$showColumn.css('opacity', 0.3).hover(
                // mouse-enter
                function(){
                    nodeshot.layout.$showColumn.fadeTo(250, 1);
                },
                // mouse-out
                function(){
                    nodeshot.layout.$showColumn.fadeTo(250, 0.3);
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
                $.cookie('nodeshot_sidebar', 'true', { expires: 365, path: __project_home__ });
            });
        }        
    },
    /*
     * nodeshot.overlay
     * Overlay, Mask, Modal message, Loading
     */
    overlay: {
        /*
        * nodeshot.overlay.addMask()
        * adds a mask over the <body>
        */
        addMask: function(opacity, closeOnClick){
            // do not add more than one mask
            if(document.getElementById('nodeshot-modal-mask') != null){
                return false;
            }
            // if opacity is not specified
            if(!opacity){
                // set default value
                opacity = 0.5
            }
            // append mask HTML element
            $('body').append('<div id="nodeshot-modal-mask"></div>');
            // initially not visible, but fades in
            var mask = $('#nodeshot-modal-mask');
            mask.css({
                opacity: 0,
                display: 'block'
            }).animate({
                opacity: opacity
            }, 500);
            // if closeOnClick == true bind click event that closes javascript stuff
            if(closeOnClick){
                mask.click(function(e){
                    nodeshot.overlay.removeMask();
                    // if dialog is open close it
                    if(nodeshot.layout.$dialog){
                        nodeshot.dialog.close();
                    }
                })
            }
        },
        /*
        * nodeshot.overlay.removeMask()
        * rermoves the mask
        */
        removeMask: function(){
            // cache jquery object
            var mask = $('#nodeshot-modal-mask');
            // stop here if no mask
            if(mask.length < 1){ return false }
            // fadeOut and remove the mask
            mask.fadeOut(500, function(){
                mask.remove();
            });
        },
        /*
        * nodeshot.overlay.appendLoading()
        * append Loading gif to the body
        */
        appendLoading: function(){
            // preload ajax-loader.gif
            $('body').append('<img src="'+__project_home__+'media/images/ajax-loader.gif" alt="" id="nodeshot-ajaxloader" />');
            nodeshot.layout.$loading = $('#nodeshot-ajaxloader');
        },
        /*
        * nodeshot.overlay.showLoading()
        * shows hidden loading gif appended previously
        */
        showLoading: function(){
            nodeshot.layout.$loading.css({
                left: nodeshot.layout.horizontalCenter(nodeshot.layout.$loading),
                top: nodeshot.layout.verticalCenter(nodeshot.layout.$loading)
            });
        },
        /*
        * nodeshot.overlay.hideLoading()
        * hides Loading gif
        */
        hideLoading: function(){
            nodeshot.layout.$loading.css('top', '-9999px');
        },
        /*
        * nodeshot.overlay.open()
        * opens overlay with data and positions to the center of the window
        */
        open: function(data, closeOnClick, callback){
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
        },
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
        },
        /*
        * nodeshot.overlay.centerVertically(animate, duration)
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
        },
        /*
        * nodeshot.overlay.bindCancelButton()
        * binds actions to the cancel button of an overlay
        */
        bindCancelButton: function(){
            $('#cancel').click(function(){
                nodeshot.overlay.close();
            });
        },
        /*
        * nodeshot.overlay.bindSubmitForm()
        * binds actions to the submit event of an overlay
        */
        bindSubmitForm: function(action){
            $('#nodeshot-form').submit(function(e){
                // cache current form
                form = $(this);
                e.preventDefault();
                // avoid duplicate emails by setting/checking sending property
                if(!nodeshot.sending){
                    // pass form
                    action(form);
                    // set sending to true to avoid duplicate submits
                    nodeshot.sending = true;
                }
            });
        },
        /*
        * nodeshot.overlay.close()
        * binds actions to the submit event of an overlay
        */
        close: function(){
            nodeshot.overlay.removeMask();
            nodeshot.layout.$overlay.remove();
            nodeshot.layout.$overlay = false;
            nodeshot.layout.$overlayInner = false;
            // reset dimensions
            nodeshot.layout.setFullScreen();
            //$('#addnode').button('option', 'label', 'Aggiungi un nuovo nodo');
            // TODO: move clickListenerHandle inside the nodeshot javascript object
            if (clickListenerHandle) {
                google.maps.event.removeListener(clickListenerHandle);
                clickListenerHandle = null;
            }
            // delete any address marker
            if(nodeshot.gmap.addressMarker){
                nodeshot.gmap.removeAddressMarker();                
            }
        }
    },
    gmap:{
        removeAddressMarker: function(){
            nodeshot.gmap.addressMarker.setMap(null);
            delete nodeshot.gmap.addressMarker;
        }
    },
    /*
    * nodeshot.dialog
    * handles messages to the user
    */
    dialog: {
        /*
        * nodeshot.dialog.open()
        */
        open: function(message, callback){
            // add HTML elements
            $('body').append('<div id="nodeshot-modal"><div id="nodeshot-modal-message">'+message+'</div><a class="button green" id="nodeshot-modal-close">ok</a></div>');
            // cache jquery object
            nodeshot.layout.$dialog = $('#nodeshot-modal');
            // add mask after $container has been cached
            nodeshot.overlay.addMask(0.5, true);
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
            // bind key press event
            nodeshot.layout.$body.bind('keyup', function(e) {
                var code = (e.keyCode ? e.keyCode : e.which);
                // if pressing enter
                if (code == 13 || code == 27){
                    nodeshot.dialog.close(callback);
                    nodeshot.layout.$body.unbind('keyup');
                }
            });
            // bind close event
            $('#nodeshot-modal-close').click(function(){
                nodeshot.dialog.close(callback);
            });
        },
        /*
        * nodeshot.dialog.close()
        */
        close: function(callback){
            // fade out and remove
            nodeshot.layout.$dialog.fadeOut(500, function(){
                nodeshot.layout.$dialog.remove();
                nodeshot.layout.$dialog = false;
            });
            nodeshot.overlay.removeMask();
            // execute callback if any
            if(callback){
                callback();
            }
        }
    },
    /*
     * nodeshot.contact
     * Contact node
     */
    contact: {
        /*
        * nodeshot.contact.init()
        * opens an overlay with the form to contact a node and binds the submit and cancel buttons
        */
        init: function(url){
            nodeshot.overlay.addMask(0.7);
            nodeshot.overlay.showLoading();
            // ajax get
            $.get(url, function(data) {
                nodeshot.overlay.hideLoading();
                nodeshot.overlay.open(data)
                // remember we are not using0 $.live() to optimize performance
                nodeshot.overlay.bindCancelButton();
                nodeshot.overlay.bindSubmitForm(function(form){
                    nodeshot.contact.submit(url, form);
                });
            });
        },
        /*
        * nodeshot.contact.submit()
        * submits the form asynchronously and returns the result
        */
        submit: function(url, form){
            nodeshot.overlay.showLoading();
            $('#nodeshot-modal-mask').css({
                zIndex: 11,
                opacity: 0.7
            });
            nodeshot.layout.$overlay.css('z-index', '10');
            
            var form_data = form.serialize();
        
            $.post(url, form_data, function(data) {
                nodeshot.overlay.hideLoading();
                
                if ($(data).find('#success').length < 1) {
                    // switch back mask and overlay
                    $('#nodeshot-modal-mask').css({
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
                } else {
                    $('#nodeshot-overlay-inner').fadeOut(500, function(){
                        nodeshot.dialog.open('Messaggio inviato con successo.', nodeshot.overlay.close);
                    });
                }
                // reset sending
                nodeshot.sending = false;
            });
        
            return false;
        },
        /*
        * nodeshot.contact.link()
        * binds click event that opens the overlay with the contact form
        */
        link: function(){
            $('#contact-link').click(function(e){
                // prevent link default behaviour
                e.preventDefault();
                nodeshot.contact.init(this.href);
            });
        }
    },
    /*
     * nodeshot.node
     * node functions
     */
    node: {
        /*
        * nodeshot.node.add()
        * opens a new overlay with the form to add a new node
        */
        add: function(){
            nodeshot.overlay.addMask();
            nodeshot.overlay.showLoading();
            $.get(__project_home__+'node/add/', function(data) {
                nodeshot.overlay.open(data);
                if (newMarker) {
                    $("#id_lat").val(newMarker.getPosition().lat());
                    $("#id_lng").val(newMarker.getPosition().lng());
                    removeNewMarker();
                }
                // we are not using $.live() for performance reasons
                nodeshot.overlay.bindCancelButton();
                nodeshot.overlay.bindSubmitForm(function(form){
                    nodeshot.node.submit(form);
                });
            });
        },
        /*
        * nodeshot.node.submit()
        * submits form to add a new node
        */
        submit: function(form){
            nodeshot.overlay.showLoading();
            // block form
            $('#nodeshot-modal-mask').css({
                zIndex: 11,
                opacity: 0.7
            });
            nodeshot.layout.$overlay.css('z-index', '10');
            
            var form_data = form.serialize();
        
            $.post(__project_home__+'node/add/', form_data, function(data) {
                
                nodeshot.overlay.hideLoading();
                
                if (data.length >= 10) {
                    // switch back mask and overlay
                    $('#nodeshot-modal-mask').css({
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
                } else {            
                    nodeshot.layout.$overlayInner.fadeOut(500, function(){
                        nodeshot.dialog.open('Grazie per aver inserito un nuovo nodo potenziale, ti abbiamo inviato un\'email con il link di conferma.', nodeshot.overlay.close);
                    });
                }
                nodeshot.layout.setFullScreen();
                nodeshot.sending = false;
            });
        },
        /*
        * nodeshot.node.bindChangePassword()
        * binds event to the change password link in edit node form
        */
        bindChangePassword: function(){
            $('#change-password').click(function(e){
                var $this = $(this);
                var password_field = $('#id_new_password');
                
                if($this.data('info')==undefined || $this.data('info').status==0){
                    $this.data('info', {
                        text: $this.text(),
                        status: 1
                    });
                    $this.text('annulla');
                    $('#id_new_password2').val('');
                    $('#id_fake_password').hide();
                    password_field.val('').show(500);
                    $('#verify-password').show(500);   
                }
                else{
                    $this.text($this.data('info').text);
                    $('#id_new_password2').val('');
                    $('#id_fake_password').show(500);
                    password_field.val('').hide();
                    $('#verify-password').hide();
                    $this.data('info').status = 0;
                }
            });
            
            if($('#non-field-errors').length > 0){
                $('#change-password').click();
            }
        }
    },
    
    advanced: {
        /*
        * nodeshot.advanced.init()
        * init jquery ui tabs and +info buttons in advanced node info
        */
        init: function(){
            nodeshot.overlay.firstTimeLoadingTab = true;
            $('#advanced-info').tabs({
                fx: { opacity: 'toggle', height: 'toggle', duration: 400 },
                show: function(e, ui){
                    if(nodeshot.overlay.firstTimeLoadingTab){
                        nodeshot.overlay.firstTimeLoadingTab = false;
                        nodeshot.overlay.centerVertically();
                    }
                    else{
                        nodeshot.overlay.centerVertically(true, 400);
                    }
                }
            });
            $('.toggle-info', '#advanced-info').toggle(
                function(){
                    var $this = $(this);
                    $this.parent().parent().parent().parent().find('.additional').show(300, function(){
                        nodeshot.overlay.centerVertically(true, 300)
                    });
                    $this.removeClass('green');
                    $this.addClass('red');
                    $this.text('– info');
                },
                function(){
                    var $this = $(this);
                    $this.parent().parent().parent().parent().find('.additional').hide(300, function(){
                        nodeshot.overlay.centerVertically(true, 300)
                    });
                    $this.removeClass('red');
                    $this.addClass('green');
                    $this.text('+ info');
                }
            )
        }
    },
    
    distance: {
        calculate: function(data, saved){
            if(!data){
                return false;
            }
            // ensure coords are float type
            data.from_lat = parseFloat(data.from_lat);
            data.from_lng = parseFloat(data.from_lng);
            data.to_lat = parseFloat(data.to_lat);
            data.to_lng = parseFloat(data.to_lng);
            // draw link on map and save it in a local variable
            var link = draw_link(data.from_lat, data.from_lng, data.to_lat, data.to_lng, 4);
            // calculate distance
            var distance = calc_distance(data.from_lat, data.from_lng, data.to_lat, data.to_lng, "K");
            // round distance 2 decimals
            distance = Math.round(distance*Math.pow(10,2))/Math.pow(10,2);
            // innerHTML
            $('#result').html(distance);
            // show result
            $('#result-row').fadeIn(500);
            // add distance link controls
            nodeshot.distance.add(link, data, distance, saved);
        },
        
        add: function(link, data, distance, saved){
            
            var index = this.links.push({
                link: link,
                from_name: data.from_name,
                to_name: data.to_name,
                $div: null,
                remove: function(){
                    if(nodeshot.distance.saved_links){
                        var found = false;
                        for(i=0; i<nodeshot.distance.saved_links.length; i++){
                            if(nodeshot.distance.saved_links[i] && nodeshot.distance.saved_links[i].from_name == this.from_name && nodeshot.distance.saved_links[i].to_name == this.to_name){
                                delete nodeshot.distance.saved_links[i];
                                var found = true;
                            }
                        }
                        if(found){
                            $.cookie('nodeshot_saved_distances', JSON.stringify(nodeshot.distance.saved_links), { expires: 365, path: __project_home__ });
                        }
                    }
                    this.link.setMap(null);
                    this.$div.fadeOut(500, this.$div.remove);
                    delete this.link;
                },
                hide: function(){
                    this.link.setMap(null);
                    this.$div.find('.link-hide').hide();
                    this.$div.find('.link-show').show();
                },
                show: function(){
                    this.link.setMap(map);
                    this.$div.find('.link-show').hide();
                    this.$div.find('.link-hide').show();                    
                },
                save: function(){
                    if(saved){
                        return false;
                    }
                    this.$div.find('.link-save').fadeOut(500);
                    // if no cookie
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
                    // save a cookie with the JSON string
                    $.cookie('nodeshot_saved_distances', json_string, { expires: 365, path: __project_home__ });
                }
            });
            index = index - 1;
            
            var from_link = '<a class="link-node" href="javascript:mapGoTo(\''+data.from_slug+'\')">'+data.from_name+'</a>';
            var to_link = '<a class="link-node" href="javascript:mapGoTo(\''+data.to_slug+'\')">'+data.to_name+'</a>';
            
            var html = '<div id="distance-link'+index+'" class="distance-link"><span>'+from_link+' - '+to_link+': <b>'+distance+' km</b> ';
            html = html +   '<a href="javascript:nodeshot.distance.links['+index+'].show()" class="link-show">mostra</a>';
            html = html +   '<a href="javascript:nodeshot.distance.links['+index+'].hide()" class="link-hide">nascondi</a>';
            if(!saved){
                html = html +   '<a href="javascript:nodeshot.distance.links['+index+'].save()" class="link-save">salva</a>';
            }
            html = html +   '<a href="javascript:nodeshot.distance.links['+index+'].remove()" class="link-remove">elimina</a>';
            html =html+'</span></div>';
            
            nodeshot.layout.$sideLinks.prepend(html);
            this.links[index].$div =  $('#distance-link'+index);
            this.links[index].$div.fadeIn(500);
            // layout might need this ;-)
            nodeshot.layout.setFullScreen();
        },
        
        remember: function(){
            this.cookie = $.cookie('nodeshot_saved_distances');
            if(this.cookie){
                this.saved_links = JSON.parse(this.cookie);
                for(i=0; i<this.saved_links.length; i++){
                    this.calculate(this.saved_links[i], 'saved');
                }
            }
            // potential nodes
            if($.cookie('nodeshot_potential_nodes')=='false'){
                $('#potential').attr('checked', '');
            }
            // link quality
            if($.cookie('nodeshot_link_quality')=='dbm'){
                $('#dbm').attr('checked', 'checked');
            }
            // sidebar
            if($.cookie('nodeshot_sidebar')=='false'){
                nodeshot.layout.$hideSide.trigger('click');
            }
        },
        
        links: []
    }
    
}

//function bindChangePassword(){
//    $('#change-password').click(function(e){
//        var $this = $(this);
//        var password_field = $('#id_new_password');
//        
//        if($this.data('info')==undefined || $this.data('info').status==0){
//            $this.data('info', {
//                text: $this.text(),
//                status: 1
//            });
//            $this.text('annulla');
//            $('#id_new_password2').val('');
//            $('#id_fake_password').hide();
//            password_field.val('').show(500);
//            $('#verify-password').show(500);   
//        }
//        else{
//            $this.text($this.data('info').text);
//            $('#id_new_password2').val('');
//            $('#id_fake_password').show(500);
//            password_field.val('').hide();
//            $('#verify-password').hide();
//            $this.data('info').status = 0;
//        }
//    });
//    
//    if($('#non-field-errors').length > 0){
//        $('#change-password').click();
//    }
//}

//function insertNodeInfo(){
//    nodeshot.overlay.addMask();
//    nodeshot.overlay.showLoading();
//    $.get(__project_home__+'node/add/', function(data) {
//        nodeshot.overlay.hideLoading();
//        $('body').append('<div id="nodeshot-overlay"></div>');
//        $('#nodeshot-overlay').html(data);
//        nodeshot.layout.setFullScreen();
//        if (newMarker) {
//            $("#id_lat").val(newMarker.getPosition().lat());
//            $("#id_lng").val(newMarker.getPosition().lng());
//            removeNewMarker();
//        }
//        $('#node-form-cancel').click(function(){
//            nodeshot.overlay.close();
//        });
//    });
//}

//function bindEditNode(){
    // working on it
    //$('#edit-link').click(function(e){
    //    e.preventDefault();
    //    var href = $(this).attr('href');
    //    nodeshotMask(0.7);
    //    nodeshotShowLoading();
    //    $.get(href, function(data) {
    //        nodeshotHideLoading();
    //        $('body').append('<div id="nodeshot-overlay"></div>');
    //        $('#nodeshot-overlay').html(data);
    //        form = $('#contact-form');
    //        form.css('margin-top', ($(window).height()-form.height()) / 2);
    //        nodeshot.layout.setFullScreen();
    //        $('#contact-form-cancel').live('click', function(){
    //            nodeshotclose();
    //        });
    //        $('#contact-form').live('submit', function(e){
    //            e.preventDefault();
    //            submitContactNode(node_id, $(this))
    //        });
    //    });
    //});
//}

//$("#node-form").live("submit", function() {
//    
//    nodeshot.overlay.showLoading();
//    $('#nodeshot-modal-mask').css({
//        zIndex: 11,
//        opacity: 0.7
//    });
//    $('#nodeshot-overlay').css('z-index', '10');
//    
//    var form_data = $(this).serialize();
//
//    $.post(__project_home__+'node_form', form_data, function(data) {
//        
//        nodeshot.overlay.hideLoading();
//        
//        if (data.length >= 10) {
//            // switch back mask and overlay
//            $('#nodeshot-modal-mask').css({
//                zIndex: 10,
//                opacity: 0.5
//            });
//            $('#nodeshot-overlay').css('z-index', '11');
//            //form errors
//            $('#nodeshot-overlay').html(data);
//        } else {            
//            $('#node-form').fadeOut(500, function(){
//                nodeshot.dialog.open('Grazie per aver inserito un nuovo nodo potenziale, ti abbiamo inviato un\'email con il link di conferma.', nodeshot.overlay.close);
//            });
//            /* do not redirect because is not needed
//            $.get(__project_home__+'device_form/'+data+'/',  function(data) {
//                $('#nodeshot-overlay').html(data); //all fine, go to device form    
//            });*/
//        }
//    });
//
//    return false; 
//});

//var conf_html_data = [];
//
//function is_last(conf_html_data) {
//    // True if the last for is fetched for the configuration of all the interfaces
//    var res = false;
//    $.each(conf_html_data, function(index, value) {
//        if (conf_html_data[index] != undefined) {
//            res = true;
//            if (!(conf_html_data[index].hnav4 && conf_html_data[index].interfaces))
//                res = false;
//        }
//    });
//    return res;
//}

//function append_configuration(conf_html_data) {
//    var c = $('#nodeshot-overlay'); 
//  for(var index in conf_html_data) {
//      c.append("<div class='if-configuration'>" + conf_html_data[index].hnav4 + conf_html_data[index].interfaces + "</div>");
//    }
//    $('#nodeshot-overlay').append('<input type="submit" id="configuration-form-submit" class="submit-button ui-priority-primary ui-corner-all ui-state-disabled hover" value="Salva" />');
//    $('#configuration-form-submit').button();
//}

//$("#device-form").live("submit", function() { 
//        var form_data = $(this).serialize();
//        var node_id = $('#node_id').val()
//        
//        $.post(__project_home__+'device_form/'+node_id+'/', form_data, function(data) {
//            if (data.length >= 10) {
//                $('#nodeshot-overlay').html(data); //form errors
//            } else {
//                var device_ids = data.split(',');
//                $('#nodeshot-overlay').empty();
//                
//                $.each( device_ids, function(index, value) {
//                    conf_html_data[String(value)] = [];
//                    // for each device, get HNAv4 and Interface forms
//                    $.get(__project_home__+'configuration_form?t=h4&device_id=' + value,  function(data) {
//                        // add data in array
//                        conf_html_data[String(value)].hnav4 = data;
//                        if (is_last(conf_html_data))
//                            append_configuration(conf_html_data);
//                    }); 
//                    $.get(__project_home__+'configuration_form?t=if&device_id=' + value,  function(data) {
//                        //add data in array
//                        conf_html_data[String(value)].interfaces = data;
//                        // if last data, construct html
//                        if (is_last(conf_html_data))
//                            append_configuration(conf_html_data); 
//                            
//                    }); 
//                });
//            }
//        });     
//        return false;
//});
//
//$("#configuration-form-submit").live("click", function() {
//    // for each dialog-form (interface and hnav4), submit the data and display errors if any
//    // if all the submissions are fine, then display thank you
//    var n_submitted = 0;
//    $.ajaxSetup({async:false});
//    $('.dialog-form').each( function(index) {
//        var form = $(this).find('form');
//        var form_data = form.serialize();
//        var new_device_id = $(this).find('.device-id').html();
//        var configuration_type = $(this).find('.configuration-type').html();
//        var mdiv = $(this);
//        $.post(__project_home__+'configuration_form?t='+configuration_type+'&device_id=' + new_device_id, form_data, function(data) {
//            if (data.length >= 10) {
//                mdiv.html(data);//errors
//            } else {
//               n_submitted = n_submitted + 1;
//               if (n_submitted == 2) {
//                    alert('Thank you!');
//                    window.location.href = "/";
//               }
//            }
//        });
//    });
//    $.ajaxSetup({async:true});
//});
