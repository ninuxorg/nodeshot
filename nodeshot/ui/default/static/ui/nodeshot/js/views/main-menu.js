(function(){
    'use strict';

    var ItemView = Marionette.ItemView.extend({
        tagName: 'li',
        template: '#main-menu-item-view-template',
        className: function(){
            // li element has 'dropdown' css class if has got children otherwise no class
            return this.model.get('children').length ? 'dropdown' : '';
        }
    });

    var EmptyView = Marionette.ItemView.extend({
        tagName: 'li',
        template: '#main-menu-empty-view-template'
    });

    Ns.views.Menu = Marionette.CollectionView.extend({
        id: 'main-menu-view',
        className: 'nav navbar-nav',
        tagName: 'ul',
        childView: ItemView,
        emptyView: EmptyView,

        initialize: function () {
            this.collection = Ns.db.menu;
            // re-fetch collection when user logs in or out
            this.listenTo(Ns.db.user, 'loggedin', this.fetch);
            this.listenTo(Ns.db.user, 'loggedout', this.fetch);
            this.listenTo(this.collection, 'sync', this.render);
        },

        /**
         * open first link of the menu
         */
        openFirst: function () {
            // get href of first useful link
            var a, href = this.$('a').filter(function () {
                a = $(this);
                if (!a.hasClass('.dropdown-toggle') && a.attr('href').indexOf('javascript:') < 0){
                    return true;
                }
                return false;
            }).eq(0).attr('href');
            // replace any initial hash or stuff that might cause problems to BackboneJS
            href = href.replace(/^#\//, '').replace(/^#/, '');
            Ns.router.navigate(href, { trigger: true });
        },

        /**
         * mark specified link as active
         */
        activate: function (part) {
            var parents,
                link = this.$('a').filter(function () {
                    return $(this).attr('href').match(new RegExp('.*' + part));
                });
            if (link.length && link.length < 2){
                this.deactivate();
                parents = link.parents('li');
                if (parents.length <= 1) {
                    parents.addClass('active');
                }
                else {
                    parents.filter('.dropdown').addClass('active');
                }
            }
        },

        /**
         * Remove any active link
         */
        deactivate: function () {
            this.$('li.active').removeClass('active');
        },

        /*
         * fetch collection
         */
        fetch: function(){
            this.collection.fetch();
        }
    });
})();
