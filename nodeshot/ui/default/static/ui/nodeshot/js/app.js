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
    tagName: 'article',
    className: 'center-stage multicolumn-md',
    template: '#page-template'
});

var MapView = Backbone.Marionette.ItemView.extend({
    id: 'map-container',
    template: '#map-template',
    
    onRender: function(){
        
    },
    
    onDomRefresh: function(){
        this.map = L.mapbox.map('map-js', 'examples.map-9ijuk24y').setView([42.12, 12.45], 9);
        setMapDimensions();
    }
});

Nodeshot.addRegions({
    body: '#body'
});

Nodeshot.addInitializer(function(){
    Nodeshot.page = new Page();
    
    Nodeshot.page.on('sync', function(){
        Nodeshot.body.show(new PageView({ model: Nodeshot.page }));
    });
    
    Nodeshot.page.on('error', function(model, http){
        if(http.status === 404){
            alert('the requested page was not found');
        }
        else{
            alert('there was an error while retrieving the page');
        }
    });
    
    Backbone.history.start();
});

var NodeshotController = {
    index: function(){
        Backbone.history.navigate('#pages/home');
    },
    
    page: function(slug){
        Nodeshot.page.set('slug', slug);
        Nodeshot.page.fetch();
        
        var link = $('#nav-bar a[href="#/pages/'+slug+'"]');
        if(link.length && link.parents('.dropdown').length){
            link.parents('.dropdown').addClass('active');
        }
        else{
            link.trigger('click');
        }
    }
}

var NodeshotRouter = new Marionette.AppRouter({
    controller: NodeshotController,
    appRoutes: {
        "": "index",
        "pages/:slug": "page"
    }
});

$(document).ready(function($){
    Nodeshot.start();
});