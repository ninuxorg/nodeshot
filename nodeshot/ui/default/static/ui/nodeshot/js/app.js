var Nodeshot = new Backbone.Marionette.Application();

var Page = Backbone.Model.extend({
    urlRoot : '/api/v1/pages/',
    idAttribute: 'slug',
    
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var PageView = Backbone.Marionette.ItemView.extend({
    el: '#content',
    template: '#page-template',

    initialize: function(){
        this.model.on("sync", this.render, this);
    }
});

Nodeshot.addRegions({
    content: '#content'
});

Nodeshot.addInitializer(function(){
    Nodeshot.page = new Page({ slug: 'home' });
    
    var view = new PageView({ model: Nodeshot.page });
    Nodeshot.page.fetch();
});

Nodeshot.start();