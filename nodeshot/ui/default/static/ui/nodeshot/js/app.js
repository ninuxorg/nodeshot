(function() {
    'use strict';
    
    Ns.views = {
        map: {},
        node: {}
    };

    Ns.url = function(resource){
        return Ns.settings.api + resource;
    };

    Ns.addRegions({
        body: '#body'
    });

    // localStorage check
    Ns.addInitializer(function () {
        Ns.preferences = window.localStorage || {};  // TODO: remove
    });

    // init layout
    Ns.addInitializer(function () {
        Ns.notifications = new Ns.collections.Notification();
        Ns.notificationView = new Ns.views.Notification({
            collection: Ns.notifications
        }).render();

        Ns.accountMenu = new Ns.views.Account({
            model: Ns.db.user
        });
        Ns.accountMenu.render();
        Ns.mainMenu = new Ns.views.Menu(); // renders automatically
        Ns.generalSearch = new Ns.views.Search(); // renders automatically
        Ns.onNodeClose = '#/map';  // TODO: de-uglify
    });

    // init pages
    Ns.addInitializer(function () {
        Ns.page = new Ns.models.Page();

        Ns.page.on('sync', function () {
            Ns.body.show(new Ns.views.Page({
                model: Ns.page
            }));
        });

        Ns.page.on('error', function (model, http) {
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

    Ns.controller = {
        // index
        index: function () {
            Ns.router.navigate('#pages/home', {
                trigger: true
            });
        },

        // page details
        getPage: function (slug) {
            $.toggleLoading('show');

            Ns.page.set('slug', slug);
            Ns.page.fetch();

            var link = $('#nav-bar a[href="#/pages/' + slug + '"]');

            if (link.length && link.parents('.dropdown').length) {
                link.parents('.dropdown').addClass('active');
            } else {
                link.trigger('click');
                link.parent().addClass('active');
            }
        },

        // node list
        getNodeList: function () {
            var nodes = new Ns.collections.Node();
            nodes.fetch().then(function () {
                Ns.body.show(new Ns.views.node.List({
                    model: new Backbone.Model({ collection: nodes }),
                    collection: nodes
                }));
            });
            $('#nav-bar a[href="#/nodes"]').parent().addClass('active');
        },

        // node details
        getNode: function (slug) {
            var node = new Ns.models.Node({ slug: slug });
            node.fetch().then(function () {
                Ns.body.show(new Ns.views.node.Detail({
                    model: node
                }));
            });
        },

        // map view
        getMap: function () {
            if (typeof Ns.body.currentView === 'undefined' || ! (Ns.body.currentView instanceof Ns.views.map.Layout)) {
                Ns.body.show(new Ns.views.map.Layout());
            }
            else {
                Ns.body.currentView.reset();
            }
            // TODO this should be inside view
            $('#nav-bar a[href="#/map"]').trigger('click').parent().addClass('active');
        },
        
        addNode: function () {
            this.getMap();
            Ns.body.currentView.addNode();
        },

        // map node popup
        getMapPopup: function (id) {
            this.getMap();
            Ns.body.currentView.content.currentView.openLeafletPopup(id);
        },

        // user profile view
        getUser: function (username) {
            var user = new Ns.models.User({ username: username });

            user.fetch()
            .done(function () {
                Ns.body.show(new Ns.views.Profile({
                    model: user
                }));
            })
            .error(function (http) {
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
    };

    Ns.router = new Marionette.AppRouter({
        controller: Ns.controller,
        appRoutes: {
            '': 'index',
            '_=_': 'index', // facebook redirects here
            'pages/:slug': 'getPage',
            'map': 'getMap',
            'map/add': 'addNode',
            'map/:slug': 'getMapPopup',
            'nodes': 'getNodeList',
            'nodes/:slug': 'getNode',
            'users/:username': 'getUser'
        }
    });

    $(document).ready(function ($) {
        Ns.start();
        // menu
        $('#nav-bar').delegate('#ns-top-nav-links li a', 'click', function (e) {
            var a = $(this);
            // if href doesn't start with javascript
            if (a.attr('href').substr(0, 10) !== 'javascript') {
                // if not dropdown and not clicking again on an active link
                if (!a.hasClass('dropdown-toggle') && !a.parents('li.active').length) {
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
            Ns.preferences.staySignedIn = data.remember;

            Ns.db.user.login(data);
        });

        // sign up
        $('#js-signup-form').submit(function (e) {
            e.preventDefault();
            var form = $(this),
            data = form.serialize();

            // remove eventual errors
            form.find('.error').removeClass('error');

            $.post(Ns.url('profiles/'), data).error(function (http) {
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
                container: '#js-password-strength-message',
                viewports: {
                    progress: '.pwstrength_viewport_progress',
                    verdict: '.pwstrength_viewport_verdict'
                },
                verdicts: ['Very weak', 'Weak', 'Normal', 'Medium', 'Strong'],
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

        // create CSS classes for clusters, statuses, ecc.
        var css = _.template($('#dynamic-css-template').html());
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
                coefficient = 2.1;
            }

            dialog.css({
                width: dialog_dimensions.width,
                right: 0
            });

            // vertically align to center
            var new_height = ($(window).height() - dialog_dimensions.height) / coefficient;
            // ensure new position is greater than zero
            new_height = new_height > 0 ? new_height : 0;
            // set new height
            dialog.css('top', new_height);
        });
    });

    $(window).load(function (e) {
        $('#preloader').fadeOut(255, function () {
            // clear overflow hidden except if map view
            if (!$('#map').length) {
                $('body').removeAttr('style');
            }
        });
    });

    $(document).ajaxSend(function (event, xhr, settings) {
        if (settings.url.indexOf('notifications') > -1) {
            return;
        }
        $.toggleLoading('show');
        Ns.currentXHR = xhr;
    });

    $(document).ajaxStop(function () {
        $.toggleLoading('hide');
    });
}());
