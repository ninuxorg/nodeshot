/*  This file contains all the functions to add/modify information about a new/existing node
 */

var nodeshot = {
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
            this.$container = $('#container');
            this.$header = $('#header');
            this.$content = $('#content');
            this.$aside = $('#aside');
            this.$map = $("#map_canvas");
        },
        /*
        * nodeshot.layout.setFullScreen()
        * adds a mask over the <body>
        */
        setFullScreen: function(){
            // cache window
            var $window = $(window);
            // set content column width
            this.$content.width($window.width()-295);
            // set side column width
            this.$aside.width('295');
            // set total width
            this.$container.width($window.width());
            // set map canvas height
            this.$map.height($window.height()-this.$header.height());
        },
        /*
        * nodeshot.layout.setElementDimensions()
        * set absolute positioning to HTML elements dinamically
        */
        setElementDimensions: function(){
            this.$content.css({
                position:"absolute",
                top: this.$header.height(),
                left: 0
            });
            this.$aside.css({
                position:"absolute",
                top: this.$header.height(),
                right: 0
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
            var paddingLeft = this.getCssInt(obj.css('padding-left'));
            var paddingRight = this.getCssInt(obj.css('padding-right'));
            var borderLeft = this.getCssInt(obj.css('border-left-width'));
            var borderRight = this.getCssInt(obj.css('border-right-width'));
            width = obj.width() + paddingLeft + paddingRight + borderLeft + borderRight;
            return ($(window).width() - width) / 2;
        },
        /*
        * nodeshot.layout.verticalCenter()
        * calculates absolute top distance to center an object vertically to the window
        */
        verticalCenter: function(obj){
            var paddingTop = this.getCssInt(obj.css('padding-top'));
            var paddingBottom = this.getCssInt(obj.css('padding-bottom'));
            var borderTop = this.getCssInt(obj.css('border-top-width'));
            var borderBottom = this.getCssInt(obj.css('border-bottom-width'));
            height = obj.height() + paddingTop + paddingBottom + borderTop + borderBottom;
            return ($(window).height() - height) / 2;
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
                    // if overlay is open close it
                    if(nodeshot.layout.$overlay){
                        nodeshot.overlay.close();
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
        open: function(data){
            this.hideLoading();
            // check if overlay is not already open
            if(!nodeshot.layout.$overlay){
                $('body').append('<div id="nodeshot-overlay"></div>');   
            }
            // cache jquery object
            nodeshot.layout.$overlay = $('#nodeshot-overlay');
            // innerHTML
            nodeshot.layout.$overlay.html(data);
            // cache inner object
            var div = $('#nodeshot-overlay-inner');
            // center overlay to window
            div.css('margin-top', nodeshot.layout.verticalCenter(div));
            // update layout dimensions
            nodeshot.layout.setFullScreen();
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
            //$('#addnode').button('option', 'label', 'Aggiungi un nuovo nodo');
            // TODO: move clickListenerHandle inside the nodeshot javascript object
            if (clickListenerHandle) {
                google.maps.event.removeListener(clickListenerHandle);
                clickListenerHandle = null;
            }
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
            $('#nodeshot-overlay').css('z-index', '10');
            
            var form_data = form.serialize();
        
            $.post(url, form_data, function(data) {
                
                nodeshot.overlay.hideLoading();
                
                if ($(data).find('#success').length < 1) {
                    // switch back mask and overlay
                    $('#nodeshot-modal-mask').css({
                        zIndex: 10,
                        opacity: 0.5
                    });
                    $('#nodeshot-overlay').css('z-index', '11');
                    //form errors
                    $('#nodeshot-overlay').html(data);
                    // optimizations needed!
                    div = $('#nodeshot-overlay-inner');
                    div.css('margin-top', -25 + ($(window).height()-div.height()) / 2);
                    // rebind events because we are not using $.live()
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
        * nodeshot.node.submitNew()
        * submits form to add a new node
        */
        submit: function(form){
            nodeshot.overlay.showLoading();
            // block form
            $('#nodeshot-modal-mask').css({
                zIndex: 11,
                opacity: 0.7
            });
            $('#nodeshot-overlay').css('z-index', '10');
            
            var form_data = form.serialize();
        
            $.post(__project_home__+'node/add/', form_data, function(data) {
                
                nodeshot.overlay.hideLoading();
                
                if (data.length >= 10) {
                    // switch back mask and overlay
                    $('#nodeshot-modal-mask').css({
                        zIndex: 10,
                        opacity: 0.5
                    });
                    $('#nodeshot-overlay').css('z-index', '11');
                    //form errors
                    $('#nodeshot-overlay').html(data);
                    // bind events again because we are not using $.live()
                    nodeshot.overlay.bindCancelButton();
                    nodeshot.overlay.bindSubmitForm(function(form){
                        nodeshot.node.submit(form);
                    });
                } else {            
                    $('#nodeshot-overlay-inner').fadeOut(500, function(){
                        nodeshot.dialog.open('Grazie per aver inserito un nuovo nodo potenziale, ti abbiamo inviato un\'email con il link di conferma.', nodeshot.overlay.close);
                    });
                }
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
    
    links: {
        //temporary: []
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
