var Page = Backbone.Model.extend({
    urlRoot: '/api/v1/pages/',
    idAttribute: 'slug',

    url: function () {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var Node = Backbone.Model.extend({
    urlRoot: '/api/v1/nodes/',
    idAttribute: 'slug',
    
    defaults: {
        "relationships": false
    },

    url: function () {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var User = Backbone.Model.extend({
    urlRoot: '/api/v1/profiles/',
    idAttribute: 'username',
    
    defaults: {
        "avatar": "http://www.gravatar.com/avatar/default"
    },

    url: function () {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});