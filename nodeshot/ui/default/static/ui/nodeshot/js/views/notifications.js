(function () {
    'use strict';

    var ItemView = Marionette.ItemView.extend({
        template: '#notification-item-template',
        tagName: 'li',
        className: function (){
            return (this.model.get('is_read')) ? 'read' : 'unread';
        },

        onRender: function (e) {
            $(this.el).attr('data-cid', this.model.cid);
        }
    }),
    EmptyView = Marionette.ItemView.extend({
        template: '#notification-empty-template'
    });

    Ns.views.Notification = Marionette.CompositeView.extend({
        template: '#notifications-template',
        childView: ItemView,
        emptyView: EmptyView,
        childViewContainer: '#js-notifications-container',
        events: { 'click li': 'action' },
        collectionEvents: { 'sync': 'countUnread' },
        ui: { 'scroller': '.scroller' },

        initialize: function () {
            this.collection = new Ns.collections.Notification();
            // listens when user status changes to fetch notifications
            this.listenTo(Ns.db.user, 'loggedin', this.fetch);
            this.listenTo(Ns.db.user, 'loggedin', this.storeExternalReferences);
            // fetch when collection is synced
            this.listenTo(this.collection, 'reset', this.render);
            if (Ns.db.user.isAuthenticated()) { this.fetch(); }
            // setPosition on resize
            $(window).on("resize.notifications", _.bind(this.setPosition, this));
            this.storeExternalReferences();
        },

        storeExternalReferences: function () {
            // external references
            this.ext = {
                'regionEl': Ns.notifications.$el,
                'button': $('#top-bar .notifications'),
                'counter': Ns.account.currentView.ui.notificationsCounter
            }
        },

        onShow: function () {
            // avoid propagating click or notification panel will close
            this.$el.click(function (e) { e.stopPropagation() });
        },

        onRender: function () {
            // The axis option is for setting the dimension in
            // which the scrollbar should operate.
            this.ui.scroller.scroller({ trackMargin: 6 });
            // show or hide unread counter
            this.countUnread();
        },

        /*
         * fetch only if necessary (if user is authenticated)
         */
        fetch: function () {
            if (Ns.db.user.isAuthenticated()) {
                this.collection.fetch({ reset: true });
            }
        },

        /*
         * trigger notification action
         */
        action: function (e) {
            var target = $(e.target), li;
            if (target.prop('tagName').toUpperCase() === 'LI'){
                li = target;
            }
            else {
                li = target.parents('li');
            }
            var notification = this.collection.get({ cid: li.attr('data-cid') }).toJSON(),
                prefix = notification.type.split('_')[0],
                deleted = notification.type.indexOf('deleted') >= 0;
            if (prefix === 'node' && deleted === false) {
                // open node
                Ns.router.navigate('nodes/' + notification.related_object, { trigger: true });
            }
            else if (prefix === 'custom' || deleted === true) {
                $.createModal({ message: notification.text });
            }
            // trigger closure of notifications panel;
            $('body > header').trigger('click');
        },

        /*
         * open notifications panel
         */
        openPanel: function (e) {
            e.preventDefault();
            var notifications = this.ext.regionEl,
                self = this;
            // show panel if hidden
            if (notifications.is(':hidden')) {
                this.setPosition();
                notifications.fadeIn(255, function () {
                    // prepare scroller
                    self.ui.scroller.scroller('reset');
                    // clicking anywhere else closes the panel
                    $('html').one('click', function () {
                        notifications.fadeOut(150, function(){
                            self.collection.read();
                        });
                    });
                });
            } else {
                notifications.fadeOut(150);
            }
        },

        /*
         * position the notification panel properly
         */
        setPosition: function () {
            if (this.ext.button.length) {
                var button = this.ext.button,
                    panel = this.ext.regionEl,
                    left = button.offset().left,
                    button_width = button.outerWidth(),
                    notifications_width = panel.getHiddenDimensions().width;
                panel.css('left', left - notifications_width / 2 + button_width / 2);
            }
        },

        /*
         * write notification count and show if greater than 0
         */
        countUnread: function (e) {
            var counter = this.ext.counter,
                unread = this.collection.getUnreadCount();
            // show or hide unread counter
            counter.html(unread).toggle(unread > 0);
        }
    });
})();
