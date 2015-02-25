(function(){
    'use strict';

    Ns.views.AccountMenu = Marionette.ItemView.extend({
        tagName: 'ul',
        template: '#account-menu-template',
        events: {
            'click #js-logout': 'logout',
            'click .notifications': 'openNotificationsPanel',
            'click .icon-search': 'focusSearch'
        },
        // listen to models change and update accordingly
        // used for login/logout rendering
        modelEvents: {
            'loggedin': 'render',
            'logout': 'render'
        },

        ui: {
            'notificationsCounter': '#js-notifications-count'
        },

        initialize: function(){
            this.model = Ns.db.user;
            // reference to elements that are not part of this view
            this.ext = { remember: $('#remember-signup') }
        },

        onRender: function(){
            this.staySignedInCheck();
        },

        /*
         * remember user preference on "stay signed in" checkbox
         */
        staySignedInCheck: function () {
            // check stay signed in checkbox
            this.ext.remember.prop('checked', localStorage.getObject('staySignedIn', false));
        },

        /*
         * logout
         */
        logout: function (e) {
            e.preventDefault();
            Ns.db.user.logout();
        },

        /**
         * calls method of notifications view
         */
        openNotificationsPanel: function(e) {
            Ns.notifications.currentView.openPanel(e);
        },

        /**
         * calls method of search view
         */
        focusSearch: function(e) {
            Ns.search.currentView.focusSearch(e);
        }
    });
})();
