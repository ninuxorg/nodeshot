Nodeshot.addRegions({
    body: '#body'
});

// localStorage check
Nodeshot.addInitializer(function () {
    Nodeshot.preferences = window.localStorage || {};
});

// init layout
Nodeshot.addInitializer(function () {

    Nodeshot.accountMenu = new AccountMenuView({
        model: Nodeshot.currentUser
    });
    Nodeshot.accountMenu.render();

});

// init pages
Nodeshot.addInitializer(function () {
    MapView.prototype.resetDataContainers();
    MapView.prototype.loadMapData();

    Nodeshot.page = new Page();

    Nodeshot.page.on('sync', function () {
        Nodeshot.body.close();
        Nodeshot.body.show(new PageView({
            model: Nodeshot.page
        }));
    });

    Nodeshot.page.on('error', function (model, http) {
        if (http.status === 404) {
            createModal({
                message: 'the requested page was not found'
            });
        } else {
            createModal({
                message: 'there was an error while retrieving the page'
            });
        }
    });

    Backbone.history.start();
});

var NodeshotController = {
    // index
    index: function () {
        Backbone.history.navigate('#pages/home', {
            trigger: true
        });
    },

    // page details
    getPage: function (slug) {
        toggleLoading('show');

        Nodeshot.page.set('slug', slug);
        Nodeshot.page.fetch();

        var link = $('#nav-bar a[href="#/pages/' + slug + '"]');

        // ensure no duplicate active links
        $('#nav-bar li').removeClass('active');

        if (link.length && link.parents('.dropdown').length) {
            link.parents('.dropdown').addClass('active');
        } else {
            link.trigger('click');
        }
    },

    // node details
    getNode: function (slug) {
        var node = new Node(Nodeshot.nodesNamed[slug].feature.properties);
        Nodeshot.body.close();
        Nodeshot.body.show(new NodeDetailsView({
            model: node
        }));
    },

    // map view
    getMap: function () {
        Nodeshot.body.close();
        Nodeshot.body.show(new MapView());
        $('#nav-bar a[href="#/map"]').trigger('click');
    },

    // map node popup
    getMapNode: function (slug) {
        if (typeof (Nodeshot.body.currentView) === "undefined" || Nodeshot.body.currentView.name != 'MapView') {
            this.getMap();
        }
        Nodeshot.nodesNamed[slug].openPopup();
    }
}

var NodeshotRouter = new Marionette.AppRouter({
    controller: NodeshotController,
    appRoutes: {
        "": "index",
        "_=_": "index", // facebook redirects here
        "pages/:slug": "getPage",
        "map": "getMap",
        "map/:slug": "getMapNode",
        "nodes/:slug": "getNode"
    }
});

$(document).ready(function ($) {
    Nodeshot.start();

    // login / sign in
    $('#js-signin-form').submit(function (e) {
        e.preventDefault();
        var data = $(this).serialize();

        // Login
        $.post('/api/v1/account/login/', data).error(function (http) {
            // TODO improve
            var json = http.responseJSON,
                errorMessage = 'Invalid username or password',
                zIndex = $('#signin-modal').css('z-index'); // original z-index
            $('#signin-modal').css('z-index', 1002); // temporarily change
            
            // determine correct error message to show
            errorMessage = json.non_field_errors || json.detail ||  errorMessage;
            
            createModal({
                message: errorMessage,
                successAction: function () {
                    $('#signin-modal').css('z-index', zIndex)
                } // restore z-index
            });
        }).done(function (response) {
            $('#signin-modal').modal('hide');
            // load User model which will trigger UI refresh
            Nodeshot.currentUser.set(response.user);
        });
    });

    // sign up 
    $('#js-signup-form').submit(function (e) {
        e.preventDefault();
        var form = $(this),
            data = form.serialize();

        // remove eventual errors
        form.find('.error').removeClass('error');

        $.post('/api/v1/profiles/', data).error(function (http) {
            // TODO improve
            // signup validation
            var json = http.responseJSON;

            for (key in json) {
                var input = $('#js-signup-' + key);
                if (input.length) {
                    var container = input.parent();
                    container.attr('data-original-title', json[key]);
                    container.addClass('error');
                }
            }

            form.find('.error').tooltip('show');
            form.find('.hastip:not(.error)').tooltip('hide');

        }).done(function (response) {
            $('#signup-modal').modal('hide');
            createModal({
                message: 'sent confirmation mail'
            });
        });
    });

    // signup link in sign in overlay
    $('#js-signup-link').click(function (e) {
        e.preventDefault();
        $('#signin-modal').modal('hide');
        $('#signup-modal').modal('show');
    });


    // signin link in signup overlay
    $('#js-signin-link').click(function (e) {
        e.preventDefault();
        $('#signup-modal').modal('hide');
        $('#signin-modal').modal('show');
    });

    // dismiss modal links
    $('.js-dismiss').click(function (e) {
        $(this).parents('.modal').modal('hide');
    });

    // enable tooltips
    $('.hastip').tooltip();
    
    // load full user profile
    if(Nodeshot.currentUser.get('username') !== undefined){
        Nodeshot.currentUser.fetch();
    }
});

var createModal = function (opts) {
    var template_html = $('#modal-template').html(),
        close = function () {
            $('#tmp-modal').modal('hide')
        },
        options = $.extend({
            message: '',
            successMessage: 'ok',
            successAction: function () {},
            defaultMessage: null,
            defaultAction: function () {}
        }, opts);

    $('body').append(_.template(template_html, options));

    $('#tmp-modal').modal('show');

    $('#tmp-modal .btn-success').one('click', function (e) {
        close();
        options.successAction()
    });

    $('#tmp-modal .btn-default').one('click', function (e) {
        close();
        options.defaultAction()
    });

    $('#tmp-modal').one('hidden.bs.modal', function (e) {
        $('#tmp-modal').remove();
    })
};

var toggleLoading = function (operation) {
    var loading = $('#loading');

    if (!loading.length) {
        $('body').append(_.template($('#loading-template').html(), {}));
        loading = $('#loading');

        var dimensions = loading.getHiddenDimensions();
        loading.outerWidth(dimensions.width);
        loading.css({
            left: 0,
            margin: '0 auto'
        });

        // close loading
        $('#loading .icon-close').click(function (e) {
            toggleLoading();
            if (Nodeshot.currentXHR) {
                Nodeshot.currentXHR.abort();
            }
        });
    }

    if (operation == 'show') {
        loading.fadeIn(255);
    } else if (operation == 'hide') {
        loading.fadeOut(255);
    } else {
        loading.fadeToggle(255);
    }
};

$(document).ajaxSend(function (event, xhr, settings) {
    toggleLoading('show');
    Nodeshot.currentXHR = xhr;
});

$(document).ajaxStop(function () {
    toggleLoading('hide');
});

// extend underscore with formatDate shortcut
_.formatDate = function(dateString){
	// TODO: format configurable
	return $.format.date(dateString, "dd MMMM yyyy - HH:mm")
};