(function() {
    'use strict';

    Ns.views = {
        map: {},
        node: {},
        layer: {}
    };

    // auxiliary object that keeps some details about the state of the app
    Ns.state = {
        currentAjaxRequest: null,  // needed to cancel an xhr request
        autoToggleLoading: true,  // indicates wether the loading div should be toggled automatically
        onNodeClose: 'map'  // when a node-details is closed go back on map
    };

    Ns.url = function (resource) {
        return Ns.settings.api + resource;
    };

    Ns.title = $('title');
    Ns.changeTitle = function (title) {
        // empty prefix if title is empty
        var prefix = title.trim() !== '' ? title + ' - ' : '';
        Ns.title.text(prefix + Ns.settings.siteName);
    };

    /**
     * web analytics
     */
    Ns.track = function () {
        var fragment = window.location.hash.substr(1),
            title = Ns.title.text();
        if (Ns.settings.googleAnalytics) {
            ga('send', 'pageview', {
                  'page': fragment,
                  'title': title
            });
        }
        if (Ns.settings.piwikAnalytics) {
            _paq.push(['setDocumentTitle', title]);
            _paq.push(['trackPageView', fragment]);
        }
    };

    Ns.addRegions({
        menu: '#ns-top-nav-links',
        search: '#general-search',
        account: '#main-actions',
        notifications: '#notifications',
        body: '#body'
    });

    // main initializers
    Ns.addInitializer(function () {
        Ns.account.show(new Ns.views.AccountMenu());
        Ns.menu.show(new Ns.views.Menu());
        Ns.search.show(new Ns.views.Search());
        Ns.notifications.show(new Ns.views.Notification());
        // empty node cache when user logs in / logs out
        // needed for node can_edit
        Ns.db.user.on('loggedin loggedout', function(){ Ns.db.nodes.reset() });
        // init backbone app
        Backbone.history.start();
        // metrics
        if (Ns.settings.metrics) {
            Ns.body.on('show', function(){ Ns.graphs.init() });
        }
    });

    Ns.controller = {
        // index
        index: function () {
            Ns.menu.currentView.openFirst();
        },

        // page details
        getPage: function (slug) {
            new Ns.views.Page({ slug: slug });
        },

        // node list
        getNodeList: function () {
            new Ns.views.node.List();
        },

        // node details
        getNode: function (slug) {
            // load node from API
            Ns.views.node.Detail.loadNode(slug, function (node) {
                // show it on map
                Ns.views.map.Layout.show('showNode', [node]);
            });
        },

        // edit node
        editNode: function (slug) {
            // load node from API
            Ns.views.node.Detail.loadNode(slug, function (node) {
                // show it on map
                Ns.views.map.Layout.show('showEditNode', [node]);
            });
        },

        // map view
        getMap: function () {
            Ns.views.map.Layout.show('loadMap');
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

        // map node popup
        getMapLatLng: function (latlng) {
            this.getMap();
            Ns.body.currentView.content.currentView.goToLatLng(latlng);
        },

        // layer list
        getLayerList: function () {
            new Ns.views.layer.List();
        },

        // get layer details
        getLayer: function (slug) {
            new Ns.views.layer.Detail({ slug: slug })
        },

        // user profile view
        getUser: function (username) {
            new Ns.views.User({ username: username });
        },

        // user nodes
        getUserNodes: function (username) {
            new Ns.views.node.List({
                collection: new Ns.collections.UserNode(null, { username: username }),
                title: 'Nodes of user: ' + username,
                addNode: false,
                activateMenu: false,
                partialStats: false,
                cache: false
            });
        },

        // get account details
        getAccount: function () {
            new Ns.views.Account();
        },

        // logged in user changes password
        getAccountPassword: function () {
            new Ns.views.AccountPassword();
        },

        // reset forgotten password
        getPasswordReset: function () {
            new Ns.views.PasswordReset();
        },

        // edit profile
        getEditUser: function () {
            new Ns.views.EditUser();
        },

        getContactNode: function (slug) {
            new Ns.views.Contact(null, { type: 'nodes', slug: slug });
        },

        getContactUser: function (slug) {
            new Ns.views.Contact(null, { type: 'profiles', slug: slug });
        },

        getContactLayer: function (slug) {
            new Ns.views.Contact(null, { type: 'layers', slug: slug });
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
            'map/latlng/:latlng': 'getMapLatLng',
            'map/:slug': 'getMapPopup',
            'nodes': 'getNodeList',
            'nodes/:slug': 'getNode',
            'nodes/:slug/edit': 'editNode',
            'layers': 'getLayerList',
            'layers/:slug': 'getLayer',
            'users/:username': 'getUser',
            'users/:username/nodes': 'getUserNodes',
            'account': 'getAccount',
            'account/password/change': 'getAccountPassword',
            'account/password/reset': 'getPasswordReset',
            'account/profile/edit': 'getEditUser',
            'nodes/:slug/contact': 'getContactNode',
            'users/:slug/contact': 'getContactUser',
            'layers/:slug/contact': 'getContactLayer'
        }
    });

    $(document).ready(function ($) {
        Ns.start();

        // login / sign in
        $('#js-signin-form').submit(function (e) {
            e.preventDefault();
            var data = $(this).serializeJSON();
            // data.remember is true if "on", false otherwise
            data.remember = data.hasOwnProperty('remember') ? true : false;
            // remember choice
            localStorage.setObject('staySignedIn', data.remember);
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
                var json = http.responseJSON,
                    key;

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
                $.createModal({ message: gettext('confirmation mail sent') });
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
            $('body').removeAttr('style');
        });
    });

    $(document).ajaxSend(function (event, xhr, settings) {
        if (settings.url.indexOf('notifications') > -1) {
            return;
        }
        if (Ns.state.autoToggleLoading) {
            $.toggleLoading('show');
        }
        Ns.state.currentAjaxRequest = xhr;
    });

    $(document).ajaxStop(function () {
        $.toggleLoading('hide');
    });
}());
