(function(){
    'use strict';

    Ns.views.Page = Backbone.Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage',
        template: '#page-template'
    });
})();
