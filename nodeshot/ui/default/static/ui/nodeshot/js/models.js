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

    isAuthenticated: function(){
        return this.get('username') !== undefined;
    },

    url: function () {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var Notification = Backbone.Model.extend({
    urlRoot: '/api/v1/account/notifications/',
    
    initialize: function(){
        this.setIcon();
    },
    
    // use type attribute to differentiate icons
    setIcon: function(){
        var value = this.get('type').split('_')[0];
        this.set('icon', value);
    },

    url: function () {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/') + '?read=false';
    }
});

var NotificationCollection = Backbone.Collection.extend({
    model: Notification,
    url: '/api/v1/account/notifications/?action=all&limit=15',
    
    // needed to use pagination results as the collection
    parse: function(response) {
        return response.results;
    },
    
    getUnreadCount: function(){
        var count = 0;
        this.models.forEach(function(model){
            if(model.get('is_read') === false){
                count++;
            }
        });
        return count;
    }
});
