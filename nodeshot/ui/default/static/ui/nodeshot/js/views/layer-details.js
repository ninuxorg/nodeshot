(function(){
    'use strict';

    Ns.views.layer.Detail = Marionette.ItemView.extend({
        tagName: 'div',
        id: 'layer-details-container',
        template: '#layer-details-template',

        events: {
            'click .icon-link': 'permalink'
        },

        initialize: function (options) {
            this.model = Ns.db.layers.get(options.slug);
            // title
            Ns.changeTitle(this.model.get('name'));
            // menu element
            Ns.menu.currentView.activate('layers');
            // analytics
            Ns.track();
            // show
            Ns.body.show(this);
        },

        /*
         * prompt permalink
         */
        permalink: function(e){
            e.preventDefault();
            var text = $(e.target).attr('data-text');
            window.prompt(text, window.location.href);
        }
    });
})();
