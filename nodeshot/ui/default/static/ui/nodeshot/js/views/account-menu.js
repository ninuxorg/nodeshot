(function(){
    'use strict';

    Ns.views.Account = Marionette.ItemView.extend({
        tagName: 'ul',
        template: '#account-menu-template',
        events: {
            'click #js-logout': 'logout',
            'click .notifications': 'openNotificationsPanel'
        },
        // listen to models change and update accordingly
        // used for login/logout rendering
        modelEvents: {
            'loggedin': 'render',
            'logout': 'render'
        },

        initialize: function(){
            this.model = Ns.db.user;
            // listen to notifications collection
            this.listenTo(Ns.notifications.currentView.collection, 'sync', this.setNotificationsCount);
            // setNotificationsPosition on resize
            $(window).on("resize.account", _.bind(this.setNotificationsPosition, this));
        },

        onRender: function(){
            this.staySignedInCheck();
            this.setNotificationsCount();
        },

        /*
         * remember user preference on "stay signed in" checkbox
         */
        staySignedInCheck: function () {
            // check stay signed in checkbox
            $('#remember-signup').prop('checked', localStorage.getObject('staySignedIn', false));
        },

        /*
         * logout
         */
        logout: function (e) {
            e.preventDefault();
            Ns.db.user.logout();
        },

        /*
         * open notifications panel
         */
        openNotificationsPanel: function (e) {
            e.preventDefault();

            var notifications = $('#notifications');

            // show panel if hidden
            if (notifications.is(':hidden')) {
                this.setNotificationsPosition();

                notifications.fadeIn(255, function () {
                    // prepare scroller
                    $('#notifications .scroller').scroller('reset');

                    // clicking anywhere else closes the panel
                    $('html').one('click', function () {
                        notifications.fadeOut(150, function(){
                            Ns.notifications.currentView.collection.read();
                        });
                    });
                });
            } else {
                notifications.fadeOut(150);
            }
        },

        /*
         * positions the notification panel correclty
         */
        setNotificationsPosition: function(){
            var button = $('#top-bar .notifications'),
                panel = $('#notifications');

            if (button.length) {
                var left = button.offset().left,
                    button_width = button.outerWidth(),
                    notifications_width = panel.getHiddenDimensions().width;

                panel.css('left', left - notifications_width / 2 + button_width / 2);
            }
        },

        /*
         * write notification count and show if greater than 0
         */
        setNotificationsCount: function(e){
            var count = Ns.notifications.currentView.collection.getUnreadCount();

            if(count > 0){
                $('#js-notifications-count').html(count).show();
            }
        }
    });
})();
