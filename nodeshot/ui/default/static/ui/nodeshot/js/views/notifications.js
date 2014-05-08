NotificationItemView = Backbone.Marionette.ItemView.extend({
    name: 'NotificationItemView',
    template: '#notification-item-template',
    tagName: 'li',
    className: function(){
        return (this.model.get('is_read')) ? 'read' : 'unread'
    }
});

var NotificationEmptyView = Backbone.Marionette.ItemView.extend({
  template: '#notification-empty-template'
});

var NotificationCollectionView = Backbone.Marionette.CollectionView.extend({
    name: 'NotificationCollectionView',
    el: '#js-notifications-container',
    tagName: 'ul',
    itemView: NotificationItemView,
    emptyView: NotificationEmptyView,
    
    
    initialize: function(){
        // listens when user status changes to fetch notifications
        this.listenTo(Nodeshot.currentUser, 'change', this.fetch);
        // fetch when collection is synced
        this.listenTo(this.collection, 'sync', this.render);
    },
    
    onRender: function(){
        var scrollContainer = $('#notifications .scroller'),
            notificationsContainer = $('#notifications'),
            containerHeight = scrollContainer.height();
        
        // The axis option is for setting the dimension in
        // which the scrollbar should operate.
        scrollContainer.scroller({
            trackMargin: 6
        });
        
        notificationsContainer.click(function (e) {
            e.stopPropagation();
        });
        
        // show / hide scrollbar
        scrollContainer.mouseenter(function (e) {
            if($('#js-notifications-container').height() >= containerHeight){
                $('.scroller-bar').fadeIn(255);
            }
        }).mouseleave(function (e) {
            $('.scroller-bar').fadeOut(255);
        });
    },
    
    /*
     * fetch only if necessary (if user is authenticated)
     */
    fetch: function(){
        if(Nodeshot.currentUser.isAuthenticated()){
            this.collection.fetch();
        }
    }
});
