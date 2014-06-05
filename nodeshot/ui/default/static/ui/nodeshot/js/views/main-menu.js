var MainMenuItemView = Backbone.Marionette.ItemView.extend({
    tagName: "li",
    template: "#main-menu-item-view-template",
    className: function(){
        // li element has "dropdown" css class if has got children otherwise no class
        return this.model.get('children').length ? 'dropdown' : '';
    }
});

var MainMenuEmptyView = Backbone.Marionette.ItemView.extend({
    tagName: "li",
    template: "#main-menu-empty-view-template"
});

var MainMenuView = Backbone.Marionette.CollectionView.extend({
    el: "#main-menu-view",
    itemView: MainMenuItemView,
    emptyView: MainMenuEmptyView,

    initialize: function(){
        this.initCollection()
        // render view when collection changes
        this.listenTo(this.collection, 'sync', this.render);
        // re-fetch collection when user logs in or out
        this.listenTo(Nodeshot.currentUser, 'loggedin', this.fetch);
        this.listenTo(Nodeshot.currentUser, 'loggedout', this.fetch);
        // fetch collection for the first time
        this.fetch();
    },

    /*
     * initalize collection if not already done
     */
    initCollection: function(){
        if(this.collection === undefined){
            this.collection = new MenuItemCollection();
        }
    },

    /*
     * fetch collection
     */
    fetch: function(){
        this.collection.fetch();
    }
});
