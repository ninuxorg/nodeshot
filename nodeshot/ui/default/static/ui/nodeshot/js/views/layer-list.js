(function(){
    'use strict';

    var ItemView = Marionette.ItemView.extend({
        tagName: "tr",
        template: "#layer-list-row-template"
    });

    var EmptyView = Marionette.ItemView.extend({
        tagName: "tr",
        template: "#layer-list-empty-template"
    });

    Ns.views.layer.List = Marionette.CompositeView.extend({
        tagName: 'article',
        className: 'center-stage',
        id: 'layer-list',
        template: '#layer-list-template',
        childView: ItemView,
        childViewContainer: '#js-rows',
        emptyView: EmptyView,

        initialize: function () {
            this.collection = Ns.db.layers;
            Ns.body.show(this);
        },

        onShow: function(){
            // title tag
            Ns.changeTitle(gettext('Layer list'));
            // mark nodes menu link as active
            Ns.menu.currentView.activate('layers');
            // analytics
            Ns.track();
        }
    });
})();
