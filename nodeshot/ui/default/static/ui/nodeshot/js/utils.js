/* --- gobal utility functions --- */
(function() {
    'use strict';

    // add setObject to localStorage for automatic JSON conversion
    Storage.prototype.setObject = function (key, value) {
        this.setItem(key, JSON.stringify(value));
    };

    // add getObject to localStorage for automatic JSON conversion
    Storage.prototype.getObject = function (key, fallback) {
        var value = this.getItem(key);
        return value ? JSON.parse(value) : fallback;
    };

    // implement String trim for older browsers
    if (!String.prototype.trim) {
        String.prototype.trim = $.trim;
    }

    // extend jquery to be able to retrieve a cookie
    $.getCookie = function (name) {
        var cookieValue = null,
        cookies,
        cookie,
        i;

        if (document.cookie && document.cookie !== '') {
            cookies = document.cookie.split(';');

            for (i = 0; i < cookies.length; i += 1) {
                cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    $.csrfSafeMethod = function (method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    $.sameOrigin = function (url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host, // host + port
        protocol = document.location.protocol,
        srOrigin = '//' + host,
        origin = protocol + srOrigin;
        // Allow absolute or scheme relative URLs to same origin
        return (url === origin || url.slice(0, origin.length + 1) === origin + '/') ||
        (url === srOrigin || url.slice(0, srOrigin.length + 1) === srOrigin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
    };

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!$.csrfSafeMethod(settings.type) && $.sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", $.getCookie('csrftoken'));
            }
        }
    });

    // Converts from degrees to radians.
    Math.radians = function (degrees) {
        return degrees * Math.PI / 180;
    };

    // Converts from radians to degrees.
    Math.degrees = function (radians) {
        return radians * 180 / Math.PI;
    };

    _.mixin({
        /**
         * Convert new lines to HTML <br>
         * https://gist.github.com/toekneestuck/1878713
         */
        nl2br: function (str, is_xhtml) {
            var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';
            return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + breakTag + '$2');
        },

        /*
        * convert rating_avg to an array of 5 elements
        * in which each element is a string that indicates
        * whether the start should be displayed as "full", "half" or "empty"
        */
        numberTo5Stars: function(value){
            // init empty array that will store results
            var stars = [],
            i;
            // populate array
            for(i=1; i<=5; i++){
                if(value >= 0.89){
                    stars.push('full');
                }
                else if(value >= 0.39){
                    stars.push('half');
                }
                else{
                    stars.push('empty');
                }
                value--;
            }
            return stars;
        },

        /**
         * extend underscore with formatDateTime shortcut
         */
        formatDateTime: function (dateString) {
            return $.format.date(dateString, Ns.settings.dateTimeFormat);
        },

        /**
         * extend underscore with formatDate shortcut
         */
        formatDate: function (dateString) {
            return $.format.date(dateString, Ns.settings.dateFormat);
        },

        /**
        * returns true if the value is present in any of the values in the list
        * eg: does the string contains any of the words supplied?
        */
        containsAny: function (string, words) {
            var length = words.length,
                words = words.reverse(),  // reverse loop
                string = string.toLowerCase();  // case insensitive
            while (length--){
                if (string.indexOf(words[length]) > -1) {
                    return true;
                }
            }
            return false;
        }
    });

    /*
    * Toggle Loading Div
    * @param operation: string "show" or "hide"
    */
    $.toggleLoading = function (operation) {
        var loading = $('#loading'),
            dimensions;
        // create loading div if not already present
        if (!loading.length) {
            $('body').append(_.template($('#loading-template').html()));
            loading = $('#loading');
            dimensions = loading.getHiddenDimensions();
            loading.outerWidth(dimensions.width);
            loading.css({
                left: 0,
                margin: '0 auto'
            });
            // close loading
            $('#loading .icon-close').click(function (e) {
                $.toggleLoading();
                if (Ns.state.currentAjaxRequest) {
                    Ns.state.currentAjaxRequest.abort();
                }
            });
        }
        // show, hide or toggle
        if (operation === 'show') {
            loading.fadeIn(255);
        } else if (operation === 'hide') {
            loading.fadeOut(255);
        } else {
            loading.fadeToggle(255);
        }
    };

    /*
    * Get width and height of a hidden element
    * returns an object with height and width
    */
    $.fn.getHiddenDimensions = function () {
        var self = $(this),
        hidden = self, // this element is hidden
        parents,
        dimensions;
        // return immediately if element is visible
        if (self.is(':visible')) {
            return {
                width: self.outerWidth(),
                height: self.outerHeight()
            };
        }
        parents = self.parents(':hidden'); // look for hidden parent elements
        // if any hidden parent element
        if (parents.length) {
            // add to hidden collection
            hidden = $().add(parents).add(hidden);
        }
        /*
        trick all the hidden elements in a way that
        they wont be shown but we'll be able to measure their dimensions
        */
        hidden.css({
            position: 'absolute',
            visibility: 'hidden',
            display: 'block'
        });
        // store width of current element
        dimensions = {
            width: self.outerWidth(),
            height: self.outerHeight()
        }
        // reset hacked css on hidden elements
        hidden.css({
            position: '',
            visibility: '',
            display: ''
        });
        // return width
        return dimensions;
    };

    /*
    * Create Modal Dialog
    * @param options: object
    *     - message: message to return to user
    *     - successMessage: success button message
    *     - successAction: function to execute when clicking success button, defaults to void
    *     - defaultMessage: default button message, hidden by default
    *     - defaultAction: function to execute when clicking default button, defaults to void
    */
    $.createModal = function (opts) {
        var template_html = $('#modal-template').html(),
        close = function () {
            $('#tmp-modal').modal('hide');
        },
        options = $.extend({
            message: '',
            successMessage: 'ok',
            successAction: function () {},
            defaultMessage: null,
            defaultAction: function () {}
        }, opts);

        $('body').append(_.template(template_html)(options));

        $('#tmp-modal').modal('show');

        $('#tmp-modal .btn-success').one('click', function (e) {
            close();
            options.successAction();
        });

        $('#tmp-modal .btn-default').one('click', function (e) {
            close();
            options.defaultAction();
        });

        $('#tmp-modal').one('hidden.bs.modal', function (e) {
            $('#tmp-modal').remove();
        });
    };

    /*
    * mask an element so it can be closed easily
    */
    $.mask = function (element, close) {
        // both arguments required
        if (!element || !close) {
            throw ('missing required arguments');
        }
        // jQueryfy if necessary
        if (!'jquery' in element) {
            element = $(element);
        }
        // determine mask id
        var maskId = element.attr('id') + '-mask',
        // determine zIndex of mask
        zIndex = parseInt(element.css('z-index'), 10) - 1;
        // append element to body
        $('body').append('<div class="mask" id="' + maskId + '"></div>');
        // apply z-index
        $('#' + maskId).css('z-index', zIndex)
        // bind event to close
        .one('click', function () {
            close(arguments);
            $(this).remove();
        });
    };

    /*
    * synchronous $.getJSON
    */
    $.getSyncJSON = function (url, data) {
        return $.ajax({
            async: false,
            url: url,
            data: data
        }).responseJSON;
    }
}());
