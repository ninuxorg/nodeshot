/*  This file contains all the functions to add/modify information about a new/existing node
 */

var nodeshot = {
    /*
     * nodeshot.overlay
     * Overlay, Mask, Modal message, Loading
     */
    overlay: {
        /*
        * nodeshot.overlay.bindCancelButton()
        * binds actions to the cancel button of an overlay
        */
        bindCancelButton: function(){
            $('#cancel').click(function(){
                nodeshotCloseForm();
            });
        },
        /*
        * nodeshot.overlay.bindSubmitForm()
        * binds actions to the submit event of an overlay
        */
        bindSubmitForm: function(action){
            console.log(nodeshot.sending);
            $('#nodeshot-form').submit(function(e){
                // cache current form
                form = $(this);
                e.preventDefault();
                // avoid duplicate emails by setting/checking sending property
                if(!nodeshot.sending){
                    // pass form
                    action(form);
                    nodeshot.sending = true;
                }
            });
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
            nodeshotMask(0.7);
            nodeshotShowLoading();
            $.get(url, function(data) {
                nodeshotHideLoading();
                if(document.getElementById('nodeshot-overlay')==null){
                    $('body').append('<div id="nodeshot-overlay"></div>');   
                }
                $('#nodeshot-overlay').html(data);
                div = $('#nodeshot-overlay-inner');
                div.css('margin-top', -25 + ($(window).height()-div.height()) / 2);
                setDimensions();
                // remember we are not using0 $.live() to optimize performance
                nodeshot.overlay.bindCancelButton();
                nodeshot.overlay.bindSubmitForm(function(form){
                    nodeshot.contact.submit(url, form);
                });
            });
        },
        submit: function(url, form){
            nodeshotShowLoading();
            $('#nodeshot-modal-mask').css({
                zIndex: 11,
                opacity: 0.7
            });
            $('#nodeshot-overlay').css('z-index', '10');
            
            var form_data = form.serialize();
        
            $.post(url, form_data, function(data) {
                
                nodeshotHideLoading();
                
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
                        console.log(url);
                        nodeshot.contact.submit(url, form);
                    });
                } else {
                    $('#nodeshot-overlay-inner').fadeOut(500, function(){
                        nodeshotModal('Messaggio inviato con successo.', nodeshotCloseForm);
                    });
                }
                // reset sending
                nodeshot.sending = false;
            });
        
            return false;
        },
        link: function(){
            $('#contact-link').click(function(e){
                e.preventDefault();
                nodeshot.contact.init(this.href);
            });
        }
    }
}

function bindChangePassword(){
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

function insertNodeInfo(){
    nodeshotMask();
    nodeshotShowLoading();
    $.get(__project_home__+'node_form', function(data) {
        nodeshotHideLoading();
        $('body').append('<div id="nodeshot-overlay"></div>');
        $('#nodeshot-overlay').html(data);
        setDimensions();
        if (newMarker) {
            $("#id_lat").val(newMarker.getPosition().lat());
            $("#id_lng").val(newMarker.getPosition().lng());
            removeNewMarker();
        }
        $('#node-form-cancel').click(function(){
            nodeshotCloseForm();
        });
    });
}

function bindEditNode(){
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
    //        setDimensions();
    //        $('#contact-form-cancel').live('click', function(){
    //            nodeshotCloseForm();
    //        });
    //        $('#contact-form').live('submit', function(e){
    //            e.preventDefault();
    //            submitContactNode(node_id, $(this))
    //        });
    //    });
    //});
}

$("#node-form").live("submit", function() {
    
    nodeshotShowLoading();
    $('#nodeshot-modal-mask').css({
        zIndex: 11,
        opacity: 0.7
    });
    $('#nodeshot-overlay').css('z-index', '10');
    
    var form_data = $(this).serialize();

    $.post(__project_home__+'node_form', form_data, function(data) {
        
        nodeshotHideLoading();
        
        if (data.length >= 10) {
            // switch back mask and overlay
            $('#nodeshot-modal-mask').css({
                zIndex: 10,
                opacity: 0.5
            });
            $('#nodeshot-overlay').css('z-index', '11');
            //form errors
            $('#nodeshot-overlay').html(data);
        } else {            
            $('#node-form').fadeOut(500, function(){
                nodeshotModal('Grazie per aver inserito un nuovo nodo potenziale, ti abbiamo inviato un\'email con il link di conferma.', nodeshotCloseForm);
            });
            /* do not redirect because is not needed
            $.get(__project_home__+'device_form/'+data+'/',  function(data) {
                $('#nodeshot-overlay').html(data); //all fine, go to device form    
            });*/
        }
    });

    return false; 
});

var conf_html_data = [];

function is_last(conf_html_data) {
    // True if the last for is fetched for the configuration of all the interfaces
    var res = false;
    $.each(conf_html_data, function(index, value) {
        if (conf_html_data[index] != undefined) {
            res = true;
            if (!(conf_html_data[index].hnav4 && conf_html_data[index].interfaces))
                res = false;
        }
    });
    return res;
}

function append_configuration(conf_html_data) {
    var c = $('#nodeshot-overlay'); 
  for(var index in conf_html_data) {
      c.append("<div class='if-configuration'>" + conf_html_data[index].hnav4 + conf_html_data[index].interfaces + "</div>");
    }
    $('#nodeshot-overlay').append('<input type="submit" id="configuration-form-submit" class="submit-button ui-priority-primary ui-corner-all ui-state-disabled hover" value="Salva" />');
    $('#configuration-form-submit').button();
}

$("#device-form").live("submit", function() { 
        var form_data = $(this).serialize();
        var node_id = $('#node_id').val()
        
        $.post(__project_home__+'device_form/'+node_id+'/', form_data, function(data) {
            if (data.length >= 10) {
                $('#nodeshot-overlay').html(data); //form errors
            } else {
                var device_ids = data.split(',');
                $('#nodeshot-overlay').empty();
                
                $.each( device_ids, function(index, value) {
                    conf_html_data[String(value)] = [];
                    // for each device, get HNAv4 and Interface forms
                    $.get(__project_home__+'configuration_form?t=h4&device_id=' + value,  function(data) {
                        // add data in array
                        conf_html_data[String(value)].hnav4 = data;
                        if (is_last(conf_html_data))
                            append_configuration(conf_html_data);
                    }); 
                    $.get(__project_home__+'configuration_form?t=if&device_id=' + value,  function(data) {
                        //add data in array
                        conf_html_data[String(value)].interfaces = data;
                        // if last data, construct html
                        if (is_last(conf_html_data))
                            append_configuration(conf_html_data); 
                            
                    }); 
                });
            }
        });     
        return false;
});

$("#configuration-form-submit").live("click", function() {
    // for each dialog-form (interface and hnav4), submit the data and display errors if any
    // if all the submissions are fine, then display thank you
    var n_submitted = 0;
    $.ajaxSetup({async:false});
    $('.dialog-form').each( function(index) {
        var form = $(this).find('form');
        var form_data = form.serialize();
        var new_device_id = $(this).find('.device-id').html();
        var configuration_type = $(this).find('.configuration-type').html();
        var mdiv = $(this);
        $.post(__project_home__+'configuration_form?t='+configuration_type+'&device_id=' + new_device_id, form_data, function(data) {
            if (data.length >= 10) {
                mdiv.html(data);//errors
            } else {
               n_submitted = n_submitted + 1;
               if (n_submitted == 2) {
                    alert('Thank you!');
                    window.location.href = "/";
               }
            }
        });
    });
    $.ajaxSetup({async:true});
});
