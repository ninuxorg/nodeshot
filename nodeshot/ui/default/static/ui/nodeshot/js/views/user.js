(function() {
    'use strict';

    Ns.views.User = Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage',
        id: 'user-details-container',
        template: '#user-details-template',

        events: {
            // actions
            'click .actions .icon-link': 'permalink'
        },

        modelEvents: {
            'sync': 'show cache',
            'error': 'error'
        },

        initialize: function (options) {
            // get cached version or init new
            this.model = Ns.db.users.get(options.username) || new Ns.models.User();
            // if not cached
            if (this.model.isNew()) {
                // fetch from server
                this.model.set('username', options.username).fetch();
            }
            else{
                this.show();
            }
        },

        show: function () { Ns.body.show(this); },
        cache: function () { Ns.db.users.add(this.model); },
        error: function (model, http) {
            if (http.status === 404) {
                $.createModal({
                    // TODO: i18n
                    message: 'the requested page was not found'
                });
            } else {
                $.createModal({
                    // TODO: i18n
                    message: 'there was an error while retrieving the page'
                });
            }
        },

        onShow: function () {
            Ns.changeTitle(this.model.get('username'));
            Ns.menu.currentView.deactivate();
            Ns.track();
        },

        /*
        * prompt permalink
        */
        permalink: function (e) {
            e.preventDefault();
            var text = $(e.target).attr('data-text');
            window.prompt(text, window.location.href);
        }
    });
}());
