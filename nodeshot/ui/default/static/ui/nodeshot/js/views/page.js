(function(){
    'use strict';

    Ns.views.Page = Backbone.Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage',
        template: '#page-template',

        modelEvents: {
            'sync': 'show cache',
            'error': 'error'
        },

        initialize: function (options) {
            // get cached version or init new
            this.model = Ns.db.pages.get(options.slug) || new Ns.models.Page();
            // if not cached
            if (this.model.isNew()) {
                // fetch from server
                this.model.set('slug', options.slug).fetch();
            }
            else{
                this.show();
            }
        },

        show: function () { Ns.body.show(this); },
        cache: function () { Ns.db.pages.add(this.model); },
        error: function (model, http) {
            if (http.status === 404) {
                $.createModal({
                    message: gettext('the requested page was not found')
                });
            } else {
                $.createModal({
                    message: gettext('there was an error while retrieving the page')
                });
            }
        },

        onShow: function () {
            Ns.changeTitle(this.model.get('title'));
            Ns.menu.currentView.activate('pages/' + this.model.get('slug'));
            Ns.track();
        }
    });
})();
