var AccountMenuView = Backbone.Marionette.ItemView.extend({
    name: 'AccountMenuView',
    el: '#main-actions',
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
        // listen to notifications collection
        this.listenTo(Nodeshot.notifications, 'sync', this.setNotificationsCount);

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
        var remember = Nodeshot.preferences.staySignedIn,
            checked =  (remember === "true" || remember === true) ? true : false;
        $('#remember-signup').prop('checked', checked);
    },

    /*
     * logout
     */
    logout: function (e) {
        e.preventDefault();
        Nodeshot.currentUser.logout();
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
                        Nodeshot.notifications.read();
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
        var count = Nodeshot.notifications.getUnreadCount();

        if(count > 0){
            $('#js-notifications-count').html(count).show();
        }
    }
});
