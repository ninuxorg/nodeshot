(function(){
    'use strict';

    Ns.views.Page = Backbone.Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage',
        template: '#page-template',

        onShow: function () {
            Ns.menu.currentView.activate('pages/'+this.model.get('slug'));
        }
    });
})();
