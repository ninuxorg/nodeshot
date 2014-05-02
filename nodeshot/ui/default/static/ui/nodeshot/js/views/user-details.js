var UserDetailsView = Backbone.Marionette.ItemView.extend({
    name: 'UserDetailsView',
    tagName: 'article',
    className: 'center-stage',
    id: 'user-details-container',
    template: '#user-details-template',
    
    events: {
        // actions
        'click .actions .icon-link': 'permalink'
    },
    
    modelEvents: {
        'change': 'render'
    },
    
    /*
     * prompt permalink
     */
    permalink: function(e){
        e.preventDefault();
        var text = $(e.target).attr('data-text');
        window.prompt(text, window.location.href)
    }
});
