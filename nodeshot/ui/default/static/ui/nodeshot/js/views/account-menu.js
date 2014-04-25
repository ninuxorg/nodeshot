var AccountMenuView = Backbone.Marionette.ItemView.extend({
    name: 'AccountMenuView',
    el: '#main-actions',
    //className: 'center-stage multicolumn-md',
    template: '#account-menu-template',

    events: {
        'click #js-logout': 'logout',
        'click .notifications': 'openNotificationsPanel'
    },
    
    // listen to models change and update accordingly
    // used for login/logout rendering
    modelEvents: {
        'change': 'render'
    },

    initialize: function () {
        this.truncateUsername();
    },

    /*
     * truncate long usernames
     */
    truncateUsername: function () {
        var username = this.model.get('username');

        if (typeof (username) !== 'undefined' && username.length > 15) {
            // add an ellipsis if username is too long
            var truncated = username.substr(0, 13) + "&hellip;";
            // update model
            this.model.set('username', truncated);
        }
    },

    /*
     * logout
     */
    logout: function (e) {
        e.preventDefault();
        Nodeshot.currentUser.clear();
        $.post('api/v1/account/logout/').error(function () {
            // TODO: improve!
            createModal({
                message: 'problem while logging out'
            });
        });
    },

    /*
     * open notifications panel
     */
    openNotificationsPanel: function (e) {
        e.preventDefault();

        var notifications = $('#notifications');

        // show panel if hidden
        if (notifications.is(':hidden')) {
            setNotificationsLeft();

            notifications.fadeIn(255, function () {
                // prepare scroller
                $('#notifications .scroller').scroller('reset');

                // clicking anywhere else closes the panel
                $('html').one('click', function () {
                    notifications.fadeOut(150);
                });
            });
        } else {
            notifications.fadeOut(150);
        }
    }
});