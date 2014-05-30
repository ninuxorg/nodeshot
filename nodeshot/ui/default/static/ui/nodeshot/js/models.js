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

var NodeCollection = Backbone.PageableCollection.extend({
    model: Node,
    url: '/api/v1/nodes/',

    // Any `state` or `queryParam` you override in a subclass will be merged with
    // the defaults in `Backbone.PageableCollection` 's prototype.
    state: {
        pageSize: 50,
        firstPage: 1,
        currentPage: 1
    },

    queryParams: {
        currentPage: "page",
        pageSize: "limit",
        totalRecords: "count"
    },

    hasNextPage: function(){
        return this.next !== null;
    },

    hasPreviousPage: function(){
        return this.previous !== null;
    },

    getNumberOfPages: function(){
        var total = this.count,
            size = this.state.pageSize;

        return Math.ceil(total / size)
    },

    search: function(q){
        this.searchTerm = q;
        return this.getPage(1, {
            data: { search: q },
            processData: true
        });
    },

    // needed to use pagination results as the collection
    parse: function(response) {
        this.count = response.count;
        this.next = response.next;
        this.previous = response.previous;
        return response.results;
    },

    initialize: function(){
        this.searchTerm = '';
    }
});

var User = Backbone.Model.extend({
    urlRoot: '/api/v1/profiles/',
    idAttribute: 'username',

    defaults: {
        "avatar": "http://www.gravatar.com/avatar/default"
    },

    initialize: function(){
        this.setTruncatedUsername();
    },

    /*
     * truncate long usernames
     */
    setTruncatedUsername: function () {
        var username = this.get('username');

        if (typeof (username) !== 'undefined' && username.length > 15) {
            // add an ellipsis if username is too long
            username = username.substr(0, 13) + "&hellip;";
        }

        // update model
        this.set('truncatedUsername', username);
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

    /*
     * use type attribute to differentiate icons
     */
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

    /*
     * get number of unread notifications
     */
    getUnreadCount: function(){
        var count = 0;
        this.models.forEach(function(model){
            if(model.get('is_read') === false){
                count++;
            }
        });
        return count;
    },

    /*
     * mark notifications as read
     */
    read: function(){
        // skip if all notifications are already read
        if(this.getUnreadCount() > 0){
            $.get(this.url.split('?')[0]);
            this.models.forEach(function(model){
                model.set('is_read', true);
            });
            this.trigger('reset');
        }
    }
});
