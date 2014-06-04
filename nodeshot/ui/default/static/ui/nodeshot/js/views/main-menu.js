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
    emptyView: MainMenuEmptyView
});
