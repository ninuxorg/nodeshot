(function(){
    'use strict';

    var ItemView = Marionette.ItemView.extend({
        tagName: 'li',
        template: '#main-menu-item-view-template',
        className: function(){
            // li element has 'dropdown' css class if has got children otherwise no class
            return this.model.get('children').length ? 'dropdown' : '';
        }
    });

    var EmptyView = Marionette.ItemView.extend({
        tagName: 'li',
        template: '#main-menu-empty-view-template'
    });

    Ns.views.Menu = Marionette.CollectionView.extend({
        id: 'main-menu-view',
        className: 'nav navbar-nav',
        tagName: 'ul',
        childView: ItemView,
        emptyView: EmptyView,

        initialize: function(){
            this.collection = Ns.db.menu;
            // re-fetch collection when user logs in or out
            this.listenTo(Ns.db.user, 'loggedin', this.fetch);
            this.listenTo(Ns.db.user, 'loggedout', this.fetch);
            this.listenTo(this.collection, 'sync', this.render);
        },

        /*
         * fetch collection
         */
        fetch: function(){
            this.collection.fetch();
        }
    });
})();
