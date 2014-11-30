Nodeshot.addRegions({
    body: '#body'
});

// localStorage check
Nodeshot.addInitializer(function () {
    Nodeshot.preferences = window.localStorage || {};
});

// init layout
Nodeshot.addInitializer(function () {
    Nodeshot.notifications = new NotificationCollection();
    Nodeshot.notificationView = new NotificationCollectionView({
        collection: Nodeshot.notifications
    }).render();

    Nodeshot.accountMenu = new AccountMenuView({
        model: Nodeshot.currentUser
    });
    Nodeshot.accountMenu.render();

    Nodeshot.mainMenu = new MainMenuView(); // renders automatically

    Nodeshot.generalSearch = new SearchView(); // renders automatically

    Nodeshot.onNodeClose = '#/map';
});

// init pages
Nodeshot.addInitializer(function () {
    MapView.prototype.resetDataContainers();
    MapView.prototype.loadMapData();

    Nodeshot.page = new Page();

    Nodeshot.page.on('sync', function () {
        Nodeshot.body.empty();
        Nodeshot.body.show(new PageView({
            model: Nodeshot.page
        }));
    });

    Nodeshot.page.on('error', function (model, http) {
        if (http.status === 404) {
            $.createModal({
                message: 'the requested page was not found'
            });
        } else {
            $.createModal({
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
        $.toggleLoading('show');

        Nodeshot.page.set('slug', slug);
        Nodeshot.page.fetch();

        var link = $('#nav-bar a[href="#/pages/' + slug + '"]');

        if (link.length && link.parents('.dropdown').length) {
            link.parents('.dropdown').addClass('active');
        } else {
            link.trigger('click');
            link.parent().addClass('active');
        }
    },

    // node list
    getNodeList: function() {
        new NodeCollection().fetch({
            success: function(collection){
                Nodeshot.body.empty();
                Nodeshot.body.show(new NodeListView({
                    model: new Backbone.Model({ collection: collection }),
                    collection: collection
                }));
            }
        });
        $('#nav-bar a[href="#/nodes"]').parent().addClass('active');
    },

    // node details
    getNode: function (slug) {
        var node = new Node(Nodeshot.nodesNamed[slug].feature.properties);
        Nodeshot.body.empty();
        Nodeshot.body.show(new NodeDetailsView({
            model: node
        }));
    },

    // map view
    getMap: function () {
        Nodeshot.body.empty();
        Nodeshot.body.show(new MapView());
        $('#nav-bar a[href="#/map"]').trigger('click').parent().addClass('active');
    },

    // map node popup
    getMapNode: function (slug) {
        if (typeof (Nodeshot.body.currentView) === "undefined" || Nodeshot.body.currentView.name != 'MapView') {
            this.getMap();
        }
        Nodeshot.nodesNamed[slug].openPopup();
    },

    // user profile view
    getUser: function (username) {
        var user = new User({ username: username });

        user.fetch()
        .done(function(){
            Nodeshot.body.empty();
            Nodeshot.body.show(new UserDetailsView({
                model: user
            }));
        })
        .error(function(http){
            // TODO: D.R.Y.
            if (http.status === 404) {
                $.createModal({
                    message: 'the requested page was not found'
                });
            } else {
                $.createModal({
                    message: 'there was an error while retrieving the page'
                });
            }
        });

        $('#nav-bar li').removeClass('active');
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
        "nodes": "getNodeList",
        "nodes/:slug": "getNode",
        "users/:username": "getUser"
    }
});

$(document).ready(function ($) {
    Nodeshot.start();

    // menu
    $('#nav-bar').delegate('#ns-top-nav-links li a', 'click', function (e) {
        var a = $(this);
        // if href doesn't start with javascript
        if (a.attr('href').substr(0, 10) != 'javascript') {
            // if not dropdown and not clicking again on an active link
            if(!a.hasClass('dropdown-toggle') && !a.parents('li.active').length){
                $('#ns-top-nav-links li.active').removeClass('active');
            }
        }
    });

    // login / sign in
    $('#js-signin-form').submit(function (e) {
        e.preventDefault();
        var data = $(this).serializeJSON();
        // data.remember is true if "on", false otherwise
        data.remember = data.hasOwnProperty('remember') ? true : false;
        // remember choice
        Nodeshot.preferences.staySignedIn = data.remember;

        Nodeshot.currentUser.login(data);
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
            $.createModal({
                message: 'sent confirmation mail'
            });
        });
    });

    // password strength
    $('#js-signup-password').pwstrength({
        common: {
            minChar: 1
        },
        ui: {
            container: "#js-password-strength-message",
            viewports: {
                progress: ".pwstrength_viewport_progress",
                verdict: ".pwstrength_viewport_verdict"
            },
            verdicts: ["Very weak", "Weak", "Normal", "Medium", "Strong"],
            scores: [10, 17, 26, 40, 50]
        }
    }).focus(function (e) {
        $('#js-password-strength-message').fadeIn(255);
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
    if(Nodeshot.currentUser.isAuthenticated()){
        Nodeshot.currentUser.fetch();
    }

    // create status CSS classes
    css = _.template($('#status-css-template').html());
    $('head').append(css);

    $('#mobile-nav').click(function (e) {
        e.preventDefault();
    });

    $('#nav-bar').delegate('#ns-top-nav-links.in a:not(.dropdown-toggle)', 'click', function (e) {
        $('#ns-top-nav-links').collapse('hide');
    });

    // automatically center modal depending on its width
    $('body').delegate('.modal.autocenter', 'show.bs.modal', function (e) {
        var dialog = $(this).find('.modal-dialog'),
            dialog_dimensions = dialog.getHiddenDimensions(),
            coefficient = $(this).attr('data-autocenter-coefficient');

        if (!coefficient) {
            coefficient = 2.1
        }

        dialog.css({
            width: dialog_dimensions.width,
            right: 0
        });

        // vertically align to center
        new_height = ($(window).height() - dialog_dimensions.height) / coefficient;
        // ensure new position is greater than zero
        new_height = new_height > 0 ? new_height : 0;
        // set new height
        dialog.css('top', new_height);
    })
});

$(window).load(function(e){
    $('#preloader').fadeOut(255, function () {
        // clear overflow hidden except if map view
        if (!$('#map').length) {
            $('body').removeAttr('style');
        }
    });
});

$(document).ajaxSend(function (event, xhr, settings) {
    if(settings.url.indexOf('notifications') > -1){
        return;
    }
    $.toggleLoading('show');
    Nodeshot.currentXHR = xhr;
});

$(document).ajaxStop(function () {
    $.toggleLoading('hide');
});
