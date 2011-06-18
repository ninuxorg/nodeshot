/*  This file contains all the functions to add/modify information about a new/existing node
 */

function insertNodeInfo(){
    $.get('/node_form', function(data) {
        $('#content').html(data);
        if (newMarker) {
            $("#id_lat").val(newMarker.getPosition().lat());
            $("#id_lng").val(newMarker.getPosition().lng());
        }
    });
}

var new_node_id = '';

$("#node-form").live("submit", function() { 
    var form_data = $(this).serialize();

    $.post('/node_form', form_data, function(data) {
        if (data.length >= 5) {
            $('#content').html(data); //form errors
        } else {
            new_node_id = data;
            $.get('/device_form?node_id=' + data,  function(data) {
                $('#content').html(data); //all fine, go to device form    
            }); 
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
    var c = $('#content'); 
  for(var index in conf_html_data) {
      c.append("<div class='if-configuration'>" + conf_html_data[index].hnav4 + conf_html_data[index].interfaces + "</div>");
    }
    $('#content').append('<input type="submit" id="configuration-form-submit" class="submit-button ui-priority-primary ui-corner-all ui-state-disabled hover" value="Salva" />');
    $('#configuration-form-submit').button();



}

$("#device-form").live("submit", function() { 
        var form_data = $(this).serialize();
        $.post('/device_form?node_id=' + new_node_id, form_data, function(data) {
            if (data.length >= 10) {
                $('#content').html(data); //form errors
            } else {
                var device_ids = data.split(',');
                $('#content').empty();
                
                $.each( device_ids, function(index, value) {
                    conf_html_data[String(value)] = [];
                    // for each device, get HNAv4 and Interface forms
                    $.get('/configuration_form?t=h4&device_id=' + value,  function(data) {
                        // add data in array
                        conf_html_data[String(value)].hnav4 = data;
                        if (is_last(conf_html_data))
                            append_configuration(conf_html_data);
                    }); 
                    $.get('/configuration_form?t=if&device_id=' + value,  function(data) {
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
        $.post('/configuration_form?t='+configuration_type+'&device_id=' + new_device_id, form_data, function(data) {
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
