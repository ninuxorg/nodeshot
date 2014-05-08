NotificationItemView = Backbone.Marionette.ItemView.extend({
    name: 'NotificationItemView',
    template: '#notification-item-template',
    tagName: 'li',
    className: function(){
        return (this.model.get('is_read')) ? 'read' : 'unread'
    },
    
    onRender: function(e){
        $(this.el).attr('data-cid', this.model.cid);
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
    
    events:{
        'click li': 'open'
    },
    
    initialize: function(){
        // listens when user status changes to fetch notifications
        this.listenTo(Nodeshot.currentUser, 'change', this.fetch);
        // fetch when collection is synced
        this.listenTo(this.collection, 'reset', this.render);
    },
    
    onRender: function(){
        var scrollContainer = $('#notifications .scroller'),
            notificationsContainer = $('#notifications'),
            counter = $('#js-notifications-count'),
            containerHeight = scrollContainer.height(),
            unread = this.collection.getUnreadCount();
        
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
        
        counter.html(unread);
        if(unread > 0){
            counter.show();
        }
        else{
            counter.hide();
        }
    },
    
    /*
     * fetch only if necessary (if user is authenticated)
     */
    fetch: function(){
        if(Nodeshot.currentUser.isAuthenticated()){
            this.collection.fetch({ reset: true });
        }
    },
    
    /*
     * open notification
     */
    open: function(e){
        var target = $(e.target),
            li;
        
        if(target.prop('tagName').toUpperCase() == 'LI'){
            li = target;
        }
        else{
            li = target.parents('li');
        }
        
        var notification = this.collection.get({ cid: li.attr('data-cid') }).toJSON(),
            prefix = notification.type.split('_')[0];
        
        if(prefix == 'node'){
            // open node
            NodeshotController.getNode(notification.related_object);
        }
        else if(prefix == 'custom'){
            createModal({ message: notification.text });
        }
        // trigger closure of notifications panel;
        $('body > header').trigger('click');
    }
});
